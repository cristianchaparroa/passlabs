'use client';

import { useState, useRef, useEffect } from 'react';
import { aiService } from '@/app/services/aiService';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

const Chats = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isThinking, setIsThinking] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        const currentInput = input;
        setInput('');
        setIsLoading(true);

        try {
            // Prepare conversation history for ChatGPT
            const chatHistory = [...messages, userMessage].map(msg => ({
                role: msg.role,
                content: msg.content,
            }));

            // Call AI service
            const response = await aiService.sendMessage(
                chatHistory,
                setIsThinking
            );

            if (response.error) {
                // Show error message
                const errorMessage: Message = {
                    id: (Date.now() + 1).toString(),
                    role: 'assistant',
                    content: `Error: ${response.error}. Please check your API key in .env.local`,
                    timestamp: new Date(),
                };
                setMessages(prev => [...prev, errorMessage]);
            } else {
                // Show AI response
                const aiMessage: Message = {
                    id: (Date.now() + 1).toString(),
                    role: 'assistant',
                    content: response.message,
                    timestamp: new Date(),
                };
                setMessages(prev => [...prev, aiMessage]);
            }
        } catch (error) {
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Sorry, something went wrong. Please try again.',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="flex h-screen bg-zinc-50 dark:bg-zinc-900">
            {/* Sidebar */}
            <div className="hidden md:flex w-64 bg-zinc-900 border-r border-zinc-800 flex-col">
                <div className="p-4 border-b border-zinc-800">
                    <button className="w-full px-4 py-3 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-white text-sm font-medium transition-colors">
                        + New chat
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto p-2">
                    {/* Chat history would go here */}
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col">
                {/* Header */}
                <div className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 px-4 py-3">
                    <div className="max-w-3xl mx-auto flex items-center justify-between">
                        <h1 className="text-lg font-semibold text-zinc-900 dark:text-white">
                            PassLabs AI
                        </h1>
                        <button className="text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto bg-white dark:bg-zinc-900">
                    <div className="max-w-3xl mx-auto">
                        {messages.length === 0 ? (
                            <div className="flex items-center justify-center h-full px-4 py-20">
                                <div className="text-center">
                                    <h2 className="text-2xl font-semibold text-zinc-900 dark:text-white mb-2">
                                        How can I help you today?
                                    </h2>
                                    <p className="text-zinc-600 dark:text-zinc-400">
                                        Start a conversation by typing a message below
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <div className="py-8">
                                {messages.map((message) => (
                                    <div
                                        key={message.id}
                                        className={`px-4 py-6 ${
                                            message.role === 'assistant'
                                                ? 'bg-zinc-50 dark:bg-zinc-800/50'
                                                : ''
                                        }`}
                                    >
                                        <div className="max-w-3xl mx-auto flex gap-4">
                                            {/* Avatar */}
                                            <div className="flex-shrink-0">
                                                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${
                                                    message.role === 'user'
                                                        ? 'bg-indigo-600'
                                                        : 'bg-emerald-600'
                                                }`}>
                                                    {message.role === 'user' ? 'U' : 'AI'}
                                                </div>
                                            </div>
                                            {/* Message Content */}
                                            <div className="flex-1 space-y-2">
                                                <div className="text-sm font-semibold text-zinc-900 dark:text-white">
                                                    {message.role === 'user' ? 'You' : 'PassLabs AI'}
                                                </div>
                                                <div className="text-zinc-800 dark:text-zinc-200 whitespace-pre-wrap">
                                                    {message.content}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                                {isLoading && (
                                    <div className="px-4 py-6 bg-zinc-50 dark:bg-zinc-800/50">
                                        <div className="max-w-3xl mx-auto flex gap-4">
                                            <div className="flex-shrink-0">
                                                <div className="w-8 h-8 rounded-full flex items-center justify-center bg-emerald-600 text-white text-sm font-medium">
                                                    AI
                                                </div>
                                            </div>
                                            <div className="flex-1">
                                                <div className="text-sm font-semibold text-zinc-900 dark:text-white mb-2">
                                                    PassLabs AI
                                                </div>
                                                {isThinking ? (
                                                    <div className="flex items-center gap-2 text-zinc-600 dark:text-zinc-400">
                                                        <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                                        </svg>
                                                        <span className="text-sm">Thinking...</span>
                                                    </div>
                                                ) : (
                                                    <div className="flex space-x-2">
                                                        <div className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                                        <div className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                                        <div className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>
                        )}
                    </div>
                </div>

                {/* Input Area */}
                <div className="border-t border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-4">
                    <div className="max-w-3xl mx-auto">
                        <div className="relative flex items-end gap-2">
                            <textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Message PassLabs AI..."
                                rows={1}
                                className="flex-1 resize-none rounded-xl border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 px-4 py-3 text-zinc-900 dark:text-white placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 max-h-32"
                                style={{ minHeight: '48px' }}
                            />
                            <button
                                onClick={handleSend}
                                disabled={!input.trim() || isLoading}
                                className="flex-shrink-0 w-10 h-10 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:bg-zinc-300 dark:disabled:bg-zinc-700 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
                            >
                                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                </svg>
                            </button>
                        </div>
                        <p className="text-xs text-zinc-500 dark:text-zinc-400 text-center mt-2">
                            PassLabs AI can make mistakes. Check important info.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Chats;
