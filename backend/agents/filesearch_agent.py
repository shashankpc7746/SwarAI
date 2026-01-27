"""
FileSearch Agent for AI Task Automation Assistant
Comprehensive file search, open, and management with cross-platform support
"""

import os
import platform
import subprocess
import glob
import mimetypes
from pathlib import Path
from typing import Dict, List, Any, Optional, TypedDict, Tuple
from langchain.tools import BaseTool
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import urllib.parse
from datetime import datetime
from config import config

class FileSearchState(TypedDict):
    """State for the FileSearch agent workflow"""
    user_input: str
    parsed_command: Dict[str, Any]
    search_results: List[Dict[str, Any]]
    selected_file: Optional[Dict[str, Any]]
    action_type: str  # search, open, share
    response_message: str
    error: Optional[str]

class FileInfo(BaseModel):
    """File information structure"""
    name: str
    path: str
    size: int
    modified: str
    file_type: str
    mime_type: str
    is_accessible: bool

class FileSearchTool(BaseTool):
    """Advanced file search tool with fuzzy matching"""
    name: str = "file_search"
    description: str = "Search for files by name, type, or content with fuzzy matching"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize search locations without using Pydantic fields
        object.__setattr__(self, 'search_locations', self._get_search_locations())
    
    def _get_search_locations(self) -> List[str]:
        """Get platform-specific search locations - expanded to cover all common directories"""
        system = platform.system().lower()
        locations = []
        
        # Add project test files directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_files_dir = os.path.join(project_root, 'test_files')
        if os.path.exists(test_files_dir):
            locations.append(test_files_dir)
        
        if system == "windows":
            # Windows search locations - comprehensive coverage
            user_profile = os.environ.get('USERPROFILE', '')
            onedrive = os.environ.get('OneDrive', '')
            onedrive_commercial = os.environ.get('OneDriveCommercial', '')
            
            # User directories
            locations.extend([
                os.path.join(user_profile, 'Documents'),
                os.path.join(user_profile, 'Desktop'),
                os.path.join(user_profile, 'Downloads'),
                os.path.join(user_profile, 'Pictures'),
                os.path.join(user_profile, 'Videos'),
                os.path.join(user_profile, 'Music'),
                os.path.join(user_profile, 'OneDrive'),
                os.path.join(user_profile, 'Favorites'),
            ])
            
            # OneDrive locations (if configured)
            if onedrive:
                locations.extend([
                    onedrive,
                    os.path.join(onedrive, 'Documents'),
                    os.path.join(onedrive, 'Desktop'),
                    os.path.join(onedrive, 'Pictures')
                ])
            
            if onedrive_commercial:
                locations.extend([
                    onedrive_commercial,
                    os.path.join(onedrive_commercial, 'Documents')
                ])
            
            # Public directories
            locations.extend([
                'C:\\Users\\Public\\Documents',
                'C:\\Users\\Public\\Desktop',
                'C:\\Users\\Public\\Downloads',
                'C:\\Users\\Public\\Pictures',
                'C:\\Users\\Public\\Videos'
            ])
        elif system == "darwin":  # macOS
            home = os.path.expanduser('~')
            locations.extend([
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
                os.path.join(home, 'Movies'),
                os.path.join(home, 'Music'),
                '/Users/Shared'
            ])
        else:  # Linux and others
            home = os.path.expanduser('~')
            locations.extend([
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
                os.path.join(home, 'Videos'),
                os.path.join(home, 'Music'),
                '/tmp',
                '/var/tmp'
            ])
        
        # Filter to existing directories
        return [loc for loc in locations if os.path.exists(loc)]
    
    def _fuzzy_match(self, query: str, filename: str) -> float:
        """Calculate fuzzy match score between query and filename"""
        query_lower = query.lower()
        filename_lower = filename.lower()
        
        # Exact match
        if query_lower == filename_lower:
            return 1.0
        
        # Contains match
        if query_lower in filename_lower:
            return 0.8
        
        # Word boundary match
        query_words = query_lower.split()
        filename_words = filename_lower.replace('.', ' ').replace('_', ' ').replace('-', ' ').split()
        
        matching_words = sum(1 for word in query_words if any(word in fw for fw in filename_words))
        if matching_words > 0:
            return 0.6 * (matching_words / len(query_words))
        
        # Character overlap
        common_chars = set(query_lower) & set(filename_lower)
        if len(common_chars) > len(query_lower) * 0.5:
            return 0.3
        
        return 0.0
    
    def _get_file_info(self, file_path: str) -> FileInfo:
        """Get comprehensive file information"""
        try:
            stat = os.stat(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            return FileInfo(
                name=os.path.basename(file_path),
                path=file_path,
                size=stat.st_size,
                modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                file_type=os.path.splitext(file_path)[1].lower(),
                mime_type=mime_type or 'unknown',
                is_accessible=os.access(file_path, os.R_OK)
            )
        except Exception as e:
            return FileInfo(
                name=os.path.basename(file_path),
                path=file_path,
                size=0,
                modified="unknown",
                file_type="unknown",
                mime_type="unknown",
                is_accessible=False
            )
    
    def _run(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for files matching the query.
        Enhanced to intelligently detect file extensions from natural language.
        """
        results = []
        query_clean = query.strip()
        
        print(f"[DEBUG] FileSearch: Raw query: '{query_clean}'")
        
        # Check if query already has an extension (e.g., "report.pdf", "apple.pdf")
        if '.' in query_clean:
            filename_parts = query_clean.rsplit('.', 1)
            if len(filename_parts) == 2 and len(filename_parts[1]) <= 5:
                # Likely a file extension - search for this specific file in ALL locations
                print(f"[DEBUG] FileSearch: Detected explicit extension in query")
                print(f"[DEBUG] FileSearch: Will search in {len(self.search_locations)} locations")
                
                max_depth = 3  # Limit search depth to prevent hanging
                
                for location in self.search_locations:
                    print(f"[DEBUG] FileSearch: Searching in {location}")
                    location_matches = 0
                    
                    try:
                        # Use os.walk instead of glob for better performance and control
                        for root, dirs, files in os.walk(location):
                            # Limit depth
                            depth = root[len(location):].count(os.sep)
                            if depth >= max_depth:
                                dirs[:] = []  # Don't recurse deeper
                                continue
                            
                            # Search in current directory
                            for filename in files:
                                if query_clean.lower() in filename.lower():
                                    file_path = os.path.join(root, filename)
                                    
                                    try:
                                        if os.path.isfile(file_path):
                                            file_info = self._get_file_info(file_path)
                                            match_score = self._fuzzy_match(query_clean.lower(), file_info.name.lower())
                                            
                                            if match_score > 0:
                                                location_matches += 1
                                                print(f"[DEBUG] FileSearch: Match found: {file_info.name} (score: {match_score}) in {os.path.basename(location)}")
                                                results.append({
                                                    "file_info": file_info.dict(),
                                                    "match_score": match_score,
                                                    "location": location
                                                })
                                                
                                                # Limit results per location to speed up
                                                if location_matches >= 5:
                                                    break
                                    except Exception as e:
                                        print(f"[DEBUG] FileSearch: Error accessing file {filename}: {str(e)}")
                                        continue
                            
                            if location_matches >= 5:
                                break
                        
                        print(f"[DEBUG] FileSearch: Found {location_matches} matches in {os.path.basename(location)}")
                        
                    except Exception as e:
                        print(f"[DEBUG] FileSearch: Error searching {location}: {str(e)}")
                        continue
                
                # Remove duplicates and sort
                unique_results = {}
                for result in results:
                    file_path = result["file_info"]["path"]
                    if file_path not in unique_results or result["match_score"] > unique_results[file_path]["match_score"]:
                        unique_results[file_path] = result
                
                # Add modification time for sorting
                for result in unique_results.values():
                    try:
                        file_path = result["file_info"]["path"]
                        mod_time = os.path.getmtime(file_path)
                        result["mod_time"] = mod_time
                    except:
                        result["mod_time"] = 0
                
                # Sort by match score first, then by recency
                sorted_results = sorted(
                    unique_results.values(), 
                    key=lambda x: (x["match_score"], x["mod_time"]), 
                    reverse=True
                )
                
                print(f"[DEBUG] FileSearch: Found {len(sorted_results)} unique files across all locations")
                return sorted_results[:max_results]
        
        # Split query into keywords for better matching
        keywords = [kw.lower() for kw in query_clean.split() if len(kw) > 1]
        print(f"[DEBUG] FileSearch: Extracted keywords: {keywords}")
        print(f"[DEBUG] FileSearch: Search locations: {self.search_locations}")
        
        if not query_clean:
            print(f"[DEBUG] FileSearch: Empty query, returning no results")
            return []
        
        # File extension detection - map natural language to extensions
        extension_map = {
            'pdf': '.pdf',
            'word': '.docx',
            'doc': '.doc',
            'docx': '.docx',
            'excel': '.xlsx',
            'xls': '.xls',
            'xlsx': '.xlsx',
            'powerpoint': '.pptx',
            'ppt': '.ppt',
            'pptx': '.pptx',
            'text': '.txt',
            'txt': '.txt',
            'image': ['.jpg', '.jpeg', '.png', '.gif'],
            'photo': ['.jpg', '.jpeg', '.png'],
            'picture': ['.jpg', '.jpeg', '.png'],
            'jpg': '.jpg',
            'jpeg': '.jpeg',
            'png': '.png',
            'gif': '.gif',
            'mp4': '.mp4',
            'mp3': '.mp3',
            'zip': '.zip',
            'rar': '.rar'
        }
        
        detected_extensions = []
        filename_keywords = []
        
        # Separate file type keywords from filename keywords
        for keyword in keywords:
            if keyword in extension_map:
                ext = extension_map[keyword]
                if isinstance(ext, list):
                    detected_extensions.extend(ext)
                else:
                    detected_extensions.append(ext)
                print(f"[DEBUG] FileSearch: Detected extension keyword '{keyword}' -> {ext}")
            else:
                filename_keywords.append(keyword)
        
        print(f"[DEBUG] FileSearch: Filename keywords: {filename_keywords}")
        print(f"[DEBUG] FileSearch: Detected extensions: {detected_extensions}")
        
        # Search in all locations
        for location in self.search_locations:
            print(f"[DEBUG] FileSearch: Searching in {location}")
            try:
                patterns = []
                
                if detected_extensions and filename_keywords:
                    # We have both filename and extension: search for "keyword.ext"
                    print(f"[DEBUG] FileSearch: Building patterns for filename + extension")
                    for ext in detected_extensions:
                        for keyword in filename_keywords:
                            # Try different pattern combinations
                            patterns.extend([
                                f"*{keyword}*{ext}",  # apple.pdf, my_apple_file.pdf
                                f"{keyword}*{ext}",   # apple.pdf, apple_report.pdf
                                f"*{keyword}{ext}"    # myapple.pdf
                            ])
                
                elif detected_extensions and not filename_keywords:
                    # Only extension specified: search all files with that extension
                    print(f"[DEBUG] FileSearch: Building patterns for extension only")
                    for ext in detected_extensions:
                        patterns.append(f"*{ext}")
                
                elif filename_keywords and not detected_extensions:
                    # No extension detected, search by keywords only
                    print(f"[DEBUG] FileSearch: Building patterns for filename only")
                    for keyword in filename_keywords:
                        patterns.extend([
                            f"*{keyword}*",
                            f"*{keyword}*.*",
                            f"{keyword}*"
                        ])
                
                else:
                    # Fallback: use full query
                    print(f"[DEBUG] FileSearch: Using fallback patterns")
                    patterns.extend([
                        f"*{query_clean}*",
                        f"*{query_clean}*.*"
                    ])
                
                # Remove duplicate patterns
                patterns = list(set(patterns))
                
                # Use os.walk for faster, controlled search
                max_depth = 3
                location_matches = 0
                
                try:
                    for root, dirs, files in os.walk(location):
                        # Limit depth
                        depth = root[len(location):].count(os.sep)
                        if depth >= max_depth:
                            dirs[:] = []
                            continue
                        
                        # Search files in current directory
                        for filename in files:
                            filename_lower = filename.lower()
                            
                            # Check if any pattern matches
                            match_found = False
                            for pattern in patterns:
                                # Simple pattern matching without glob
                                pattern_clean = pattern.replace('*', '').replace('?', '')
                                if pattern_clean.lower() in filename_lower:
                                    match_found = True
                                    break
                            
                            if match_found:
                                file_path = os.path.join(root, filename)
                                try:
                                    if os.path.isfile(file_path):
                                        file_info = self._get_file_info(file_path)
                                        
                                        # Score by keyword matches
                                        keyword_score = sum(1 for kw in filename_keywords if kw in filename_lower)
                                        match_score = self._fuzzy_match(query_clean, file_info.name) + (keyword_score * 10)
                                        
                                        if match_score > 0:
                                            location_matches += 1
                                            print(f"[DEBUG] FileSearch: Match found: {file_info.name} (score: {match_score}, keywords: {keyword_score})")
                                            results.append({
                                                "file_info": file_info.dict(),
                                                "match_score": match_score,
                                                "location": location
                                            })
                                            
                                            if location_matches >= 5:
                                                break
                                except Exception as e:
                                    continue
                        
                        if location_matches >= 5:
                            break
                    
                    print(f"[DEBUG] FileSearch: Found {location_matches} matches in {os.path.basename(location)}")
                    
                except Exception as e:
                    print(f"[DEBUG] FileSearch: Error searching {location}: {str(e)}")
                    continue
                        
            except Exception as e:
                print(f"[DEBUG] FileSearch: Location error for {location}: {str(e)}")
                continue
        
        # Remove duplicates
        unique_results = {}
        for result in results:
            file_path = result["file_info"]["path"]
            if file_path not in unique_results or result["match_score"] > unique_results[file_path]["match_score"]:
                unique_results[file_path] = result
        
        # Add modification time to results for recency sorting
        for result in unique_results.values():
            try:
                file_path = result["file_info"]["path"]
                mod_time = os.path.getmtime(file_path)
                result["mod_time"] = mod_time
            except:
                result["mod_time"] = 0
        
        # Sort by match score first, then by recency (modification time)
        # This ensures best matches appear first, but recent files are prioritized within same score
        sorted_results = sorted(
            unique_results.values(), 
            key=lambda x: (x["match_score"], x["mod_time"]), 
            reverse=True
        )
        final_results = sorted_results[:max_results]
        
        print(f"[DEBUG] FileSearch: Final results: {len(final_results)} files")
        for result in final_results:
            mod_date = datetime.fromtimestamp(result['mod_time']).strftime('%Y-%m-%d %H:%M') if result.get('mod_time') else 'Unknown'
            print(f"[DEBUG] FileSearch: - {result['file_info']['name']} (score: {result['match_score']}, modified: {mod_date})")
            print(f"[DEBUG] FileSearch:   Location: {result['location']}")
        
        return final_results

class FileOpenTool(BaseTool):
    """Cross-platform file opening tool"""
    name: str = "file_open"
    description: str = "Open files using the default system application"
    
    def _run(self, file_path: str) -> Dict[str, Any]:
        """Open file with default application"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "message": f"File not found: {file_path}",
                    "error": "File not found"
                }
            
            if not os.access(file_path, os.R_OK):
                return {
                    "success": False,
                    "message": f"No permission to access: {file_path}",
                    "error": "Permission denied"
                }
            
            system = platform.system().lower()
            
            if system == "windows":
                os.startfile(file_path)
            elif system == "darwin":  # macOS
                subprocess.run(["open", file_path], check=True)
            else:  # Linux and others
                subprocess.run(["xdg-open", file_path], check=True)
            
            return {
                "success": True,
                "message": f"Successfully opened: {os.path.basename(file_path)}",
                "file_path": file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to open file: {str(e)}",
                "error": str(e)
            }

class FileShareTool(BaseTool):
    """Tool to prepare files for sharing"""
    name: str = "file_share"
    description: str = "Prepare files for sharing via WhatsApp or other platforms"
    
    def _run(self, file_path: str, recipient: str = "") -> Dict[str, Any]:
        """Prepare file for sharing"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "message": f"File not found: {file_path}",
                    "error": "File not found"
                }
            
            file_info = os.stat(file_path)
            file_size_mb = file_info.st_size / (1024 * 1024)
            
            # Check file size limitations
            if file_size_mb > 100:  # 100MB limit for WhatsApp
                return {
                    "success": False,
                    "message": f"File too large ({file_size_mb:.1f}MB). WhatsApp limit is 100MB.",
                    "error": "File too large"
                }
            
            # Prepare sharing information
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_path)[1]
            
            sharing_message = f"📁 File: {file_name}\n📏 Size: {file_size_mb:.1f}MB\n📄 Type: {file_extension}"
            
            if recipient:
                sharing_message += f"\n👤 For: {recipient}"
            
            return {
                "success": True,
                "message": f"File prepared for sharing: {file_name}",
                "file_path": file_path,
                "file_name": file_name,
                "file_size_mb": file_size_mb,
                "sharing_message": sharing_message,
                "recipient": recipient
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to prepare file: {str(e)}",
                "error": str(e)
            }

class FileSearchAgent:
    """LangGraph-powered FileSearch Agent"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        # Initialize tools
        self.search_tool = FileSearchTool()
        self.open_tool = FileOpenTool()
        self.share_tool = FileShareTool()
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for file operations"""
        
        def parse_command_node(state: FileSearchState) -> FileSearchState:
            """Parse user command to extract file operation details"""
            try:
                if 'parsed_command' not in state:
                    state['parsed_command'] = {}
                if 'error' not in state:
                    state['error'] = None
                
                system_prompt = """You are a file operation parser. Extract the following from user input:
                
                OPERATIONS:
                - search: Find files by name/type
                - open: Open a specific file
                - share: Prepare file for sharing (often with WhatsApp)
                
                IMPORTANT: For QUERY, extract the filename and file extension separately. Handle natural language file type references.
                
                Extract:
                1. Operation type (search/open/share)
                2. File query with proper filename and extension
                3. Recipient (if sharing)
                4. Additional context
                
                FILE EXTENSION RECOGNITION:
                - "PDF" or "pdf file" -> add ".pdf" extension
                - "Word" or "Word document" or "docx" -> add ".docx" extension
                - "Excel" or "spreadsheet" or "xlsx" -> add ".xlsx" extension
                - "PowerPoint" or "presentation" or "pptx" -> add ".pptx" extension
                - "text file" or "txt" -> add ".txt" extension
                - "image" or "picture" or "photo" -> can be .jpg, .png, .jpeg
                
                Examples:
                - "Find my project file" -> operation: search, query: "project"
                - "Open report.pdf" -> operation: open, query: "report.pdf"
                - "Open Apple PDF" -> operation: open, query: "apple.pdf"
                - "Open Apple PDF from file" -> operation: open, query: "apple.pdf"
                - "Find ownership document" -> operation: search, query: "ownership"
                - "Search for Excel files" -> operation: search, query: ".xlsx"
                - "Open presentation PowerPoint" -> operation: open, query: "presentation.pptx"
                - "Find report Word document" -> operation: search, query: "report.docx"
                - "Send photo.jpg to Mom" -> operation: share, query: "photo.jpg", recipient: "Mom"
                - "open Jews learning from file" -> operation: open, query: "jews learning"
                
                QUERY EXTRACTION RULES:
                - Remove: "open", "find", "search", "locate", "show", "get", "from file", "from"
                - Remove: articles like "the", "a", "an", "my", "your"
                - Convert file type words to extensions: "PDF" -> ".pdf", "Word" -> ".docx"
                - If filename + file type mentioned, combine them: "Apple PDF" -> "apple.pdf"
                - Keep it SHORT and add proper extension
                
                Return in this format:
                OPERATION: [search/open/share]
                QUERY: [SHORT filename/pattern - NO ACTION WORDS]
                RECIPIENT: [name or empty]
                CONTEXT: [additional info or empty]
                
                If unclear, return:
                ERROR: Unable to parse command"""
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=state['user_input'])
                ]
                
                response = self.llm.invoke(messages)
                response_text = response.content.strip()
                
                if "ERROR:" in response_text:
                    state['error'] = "Could not understand the file command. Please try: 'Find [filename]', 'Open [filename]', or 'Send [filename] to [contact]'"
                    return state
                
                # Parse the response
                lines = response_text.split('\n')
                operation = ""
                query = ""
                recipient = ""
                context = ""
                
                for line in lines:
                    if line.startswith("OPERATION:"):
                        operation = line.replace("OPERATION:", "").strip().lower()
                    elif line.startswith("QUERY:"):
                        query = line.replace("QUERY:", "").strip()
                    elif line.startswith("RECIPIENT:"):
                        recipient = line.replace("RECIPIENT:", "").strip()
                    elif line.startswith("CONTEXT:"):
                        context = line.replace("CONTEXT:", "").strip()
                
                if not operation or not query:
                    state['error'] = "Could not extract operation and file query. Please be more specific."
                    return state
                
                state['parsed_command'] = {
                    "operation": operation,
                    "query": query,
                    "recipient": recipient,
                    "context": context
                }
                state['action_type'] = operation
                
                return state
                
            except Exception as e:
                state['error'] = f"Error parsing command: {str(e)}"
                return state
        
        def execute_operation_node(state: FileSearchState) -> FileSearchState:
            """Execute the file operation"""
            if state.get('error'):
                return state
            
            try:
                operation = state.get('action_type', '')
                query = state.get('parsed_command', {}).get('query', '')
                recipient = state.get('parsed_command', {}).get('recipient', '')
                
                if operation == 'search':
                    # Search for files
                    results = self.search_tool._run(query, max_results=10)
                    state['search_results'] = results
                    
                    if not results:
                        state['response_message'] = f"❌ No files found matching '{query}'. Try a different search term."
                    else:
                        # Format search results with location and recency info
                        result_text = f"🔍 Found {len(results)} file(s) matching '{query}':\n\n"
                        for i, result in enumerate(results[:5], 1):
                            file_info = result['file_info']
                            size_kb = file_info['size'] / 1024
                            location = result.get('location', 'Unknown')
                            
                            # Show just the folder name from location
                            location_name = os.path.basename(location) if location != 'Unknown' else 'Unknown'
                            
                            # Get modification date
                            try:
                                mod_time = result.get('mod_time', 0)
                                if mod_time:
                                    mod_date = datetime.fromtimestamp(mod_time)
                                    # Show relative time if recent
                                    now = datetime.now()
                                    delta = now - mod_date
                                    if delta.days == 0:
                                        time_str = f"Today {mod_date.strftime('%H:%M')}"
                                    elif delta.days == 1:
                                        time_str = f"Yesterday {mod_date.strftime('%H:%M')}"
                                    elif delta.days < 7:
                                        time_str = f"{delta.days} days ago"
                                    else:
                                        time_str = mod_date.strftime('%Y-%m-%d')
                                else:
                                    time_str = "Unknown"
                            except:
                                time_str = "Unknown"
                            
                            result_text += f"{i}. � **{file_info['name']}**\n"
                            result_text += f"   📂 {location_name} • 📏 {size_kb:.1f}KB • {file_info['file_type']}\n"
                            result_text += f"   🕒 Modified: {time_str}\n\n"
                        
                        if len(results) > 5:
                            result_text += f"... and {len(results) - 5} more files\n"
                        
                        result_text += "💡 Say 'Open [filename]' to open a specific file!"
                        state['response_message'] = result_text
                
                elif operation == 'open':
                    # First search for the file
                    results = self.search_tool._run(query, max_results=5)
                    
                    if not results:
                        state['response_message'] = f"❌ File '{query}' not found. Try searching first with 'Find {query}'"
                    else:
                        # Use the best match
                        best_match = results[0]
                        file_path = best_match['file_info']['path']
                        
                        # Open the file
                        open_result = self.open_tool._run(file_path)
                        
                        if open_result['success']:
                            state['response_message'] = f"✅ {open_result['message']}\n📂 Path: {file_path}"
                            state['selected_file'] = best_match['file_info']
                        else:
                            state['response_message'] = f"❌ {open_result['message']}"
                
                elif operation == 'share':
                    # First search for the file
                    results = self.search_tool._run(query, max_results=5)
                    
                    if not results:
                        state['response_message'] = f"❌ File '{query}' not found for sharing."
                    else:
                        # Use the best match
                        best_match = results[0]
                        file_path = best_match['file_info']['path']
                        
                        # Prepare for sharing
                        share_result = self.share_tool._run(file_path, recipient)
                        
                        if share_result['success']:
                            state['response_message'] = f"📤 {share_result['message']}\n\n{share_result['sharing_message']}\n\n💡 File is ready to share!"
                            state['selected_file'] = best_match['file_info']
                            
                            # Add sharing context for WhatsApp integration
                            state['parsed_command']['sharing_info'] = share_result
                        else:
                            state['response_message'] = f"❌ {share_result['message']}"
                
                else:
                    state['error'] = f"Unknown operation: {operation}"
                
                return state
                
            except Exception as e:
                state['error'] = f"Error executing operation: {str(e)}"
                return state
        
        def generate_response_node(state: FileSearchState) -> FileSearchState:
            """Generate final response"""
            try:
                if state.get('error'):
                    state['response_message'] = f"❌ FileSearch Error: {state['error']}"
                
                return state
                
            except Exception as e:
                state['response_message'] = f"❌ Error generating response: {str(e)}"
                return state
        
        # Build the workflow graph
        workflow = StateGraph(FileSearchState)
        
        # Add nodes
        workflow.add_node("parse_command", parse_command_node)
        workflow.add_node("execute_operation", execute_operation_node)
        workflow.add_node("generate_response", generate_response_node)
        
        # Add edges
        workflow.set_entry_point("parse_command")
        
        def should_execute(state: FileSearchState) -> str:
            if state.get('error'):
                return "generate_response"
            return "execute_operation"
        
        workflow.add_conditional_edges("parse_command", should_execute)
        workflow.add_edge("execute_operation", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process file command using LangGraph workflow"""
        try:
            # Initialize state
            initial_state: FileSearchState = {
                'user_input': user_input,
                'parsed_command': {},
                'search_results': [],
                'selected_file': None,
                'action_type': '',
                'response_message': '',
                'error': None
            }
            
            # Run the workflow
            result = self.workflow.invoke(initial_state)
            
            return {
                "success": not bool(result.get('error')),
                "message": result.get('response_message', ''),
                "action_type": result.get('action_type', ''),
                "search_results": result.get('search_results', []),
                "selected_file": result.get('selected_file'),
                "parsed_command": result.get('parsed_command', {}),
                "error": result.get('error')
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ FileSearch agent error: {str(e)}",
                "action_type": "error",
                "search_results": [],
                "selected_file": None,
                "parsed_command": {},
                "error": str(e)
            }

# Global agent instance
filesearch_agent = FileSearchAgent()