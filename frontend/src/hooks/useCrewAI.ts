'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

export interface CrewAIResult {
  success: boolean;
  message: string;
  agent_used: string;
  agents_involved: string[];
  execution_time: number;
  workflow_id: string;
  results: Record<string, any>;
  timestamp: string;
  intent?: string;
  requires_popup?: boolean;
  whatsapp_url?: string;
  file_info?: any;
}

type BackendStatus = 'online' | 'offline' | 'checking';

export function useCrewAI() {
  const [backendStatus, setBackendStatus] = useState<BackendStatus>('checking');
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastResult, setLastResult] = useState<CrewAIResult | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // WebSocket connection for real-time updates
  const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(
    'ws://localhost:8000/ws',
    {
      shouldReconnect: () => true,
      reconnectInterval: 3000,
      reconnectAttempts: 10,
      onOpen: () => {
        console.log('🔌 WebSocket connected');
        setBackendStatus('online');
      },
      onClose: () => {
        console.log('🔌 WebSocket disconnected');
        setBackendStatus('offline');
      },
      onError: (event) => {
        console.error('🔌 WebSocket error:', event);
        setBackendStatus('offline');
      },
    }
  );
  
  // Handle WebSocket messages
  useEffect(() => {
    if (lastJsonMessage) {
      console.log('📬 WebSocket message received:', lastJsonMessage);
      
      const message = lastJsonMessage as any;
      
      if (message.type === 'command_result') {
        console.log('📦 Processing command result:', message.data);
        
        const resultData = message.data;
        // Ensure agents_involved is always an array
        if (!resultData.agents_involved) {
          resultData.agents_involved = [];
        }
        
        console.log('✅ Converted WebSocket result:', resultData);
        console.log('🔍 WhatsApp URL in result:', resultData.whatsapp_url);
        console.log('🔍 Results object:', resultData.results);
        
        setLastResult(resultData);
        setIsProcessing(false);
      } else if (message.type === 'pong') {
        console.log('🏠 Backend pong received - connection healthy');
        setBackendStatus('online');
      }
    }
  }, [lastJsonMessage]);
  
  // Send periodic ping to maintain connection
  useEffect(() => {
    if (readyState === ReadyState.OPEN) {
      const interval = setInterval(() => {
        sendJsonMessage({ type: 'ping' });
      }, 30000);
      
      return () => clearInterval(interval);
    }
  }, [readyState, sendJsonMessage]);
  
  const checkStatus = useCallback(async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch('http://localhost:8000/health', {
        method: 'GET',
        signal: controller.signal,
        cache: 'no-cache'
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        setBackendStatus('online');
        return true;
      } else {
        setBackendStatus('offline');
        return false;
      }
    } catch (error: any) {
      console.warn('Backend health check failed:', error.message);
      setBackendStatus('offline');
      return false;
    }
  }, []);
  
  const executeCommand = useCallback(async (command: string): Promise<CrewAIResult | null> => {
    if (!command.trim()) return null;
    
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    setIsProcessing(true);
    
    try {
      // Prefer WebSocket if available
      if (readyState === ReadyState.OPEN) {
        sendJsonMessage({
          type: 'command',
          command: command
        });
        return null; // Result will come via WebSocket
      }
      
      // Fallback to HTTP
      const controller = new AbortController();
      abortControllerRef.current = controller;
      
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, 60000); // 60 second timeout for complex workflows
      
      console.log('🚀 Executing command:', command);
      
      const response = await fetch('http://localhost:8000/process-command', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ 
          command,
          context: {},
          priority: 'normal'
        }),
        signal: controller.signal,
        cache: 'no-cache'
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result: CrewAIResult = await response.json();
      
      // Ensure agents_involved is always an array
      if (!result.agents_involved) {
        result.agents_involved = [];
      }
      
      console.log('✅ Command result:', result);
      
      setLastResult(result);
      abortControllerRef.current = null;
      
      return result;
      
    } catch (error: any) {
      console.error('❌ Command execution error:', error);
      
      let errorMessage = 'Unknown error occurred';
      if (error.name === 'AbortError') {
        errorMessage = 'Request timed out after 60 seconds';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      const errorResult: CrewAIResult = {
        success: false,
        message: `❌ Error: ${errorMessage}`,
        agent_used: 'error',
        agents_involved: [],
        execution_time: 0,
        workflow_id: 'error',
        results: { error: errorMessage },
        timestamp: new Date().toISOString()
      };
      
      setLastResult(errorResult);
      
      // Check backend status after error
      setTimeout(checkStatus, 1000);
      
      return errorResult;
      
    } finally {
      setIsProcessing(false);
      abortControllerRef.current = null;
    }
  }, [readyState, sendJsonMessage, checkStatus]);
  
  const executeWorkflow = useCallback(async (
    workflowType: string, 
    parameters: Record<string, any>
  ): Promise<CrewAIResult | null> => {
    setIsProcessing(true);
    
    try {
      console.log(`🎯 Executing ${workflowType} workflow:`, parameters);
      
      const response = await fetch('http://localhost:8000/execute-workflow', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          workflow_type: workflowType,
          parameters,
          context: {}
        }),
        cache: 'no-cache'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result: CrewAIResult = await response.json();
      
      // Ensure agents_involved is always an array
      if (!result.agents_involved) {
        result.agents_involved = [];
      }
      
      console.log('✅ Workflow result:', result);
      
      setLastResult(result);
      return result;
      
    } catch (error: any) {
      console.error('❌ Workflow execution error:', error);
      
      const errorResult: CrewAIResult = {
        success: false,
        message: `❌ Workflow error: ${error.message}`,
        agent_used: workflowType,
        agents_involved: [],
        execution_time: 0,
        workflow_id: 'error',
        results: { error: error.message },
        timestamp: new Date().toISOString()
      };
      
      setLastResult(errorResult);
      return errorResult;
      
    } finally {
      setIsProcessing(false);
    }
  }, []);
  
  const getAgentsStatus = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/agents/status', {
        cache: 'no-cache'
      });
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('Failed to get agents status:', error);
    }
    
    return null;
  }, []);
  
  return {
    backendStatus,
    isProcessing,
    lastResult,
    wsReadyState: readyState,
    executeCommand,
    executeWorkflow,
    checkStatus,
    getAgentsStatus,
    clearResult: () => setLastResult(null)
  };
}