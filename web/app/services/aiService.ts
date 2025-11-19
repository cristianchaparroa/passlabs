interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
}

interface ChatCompletionResponse {
    message: string;
    error?: string;
}

class AIService {
    private apiKey: string;
    private baseURL: string = 'https://api.openai.com/v1';

    constructor() {
        this.apiKey = process.env.NEXT_PUBLIC_OPENAI_API_KEY || '';
        
        if (!this.apiKey) {
            console.warn('OpenAI API key not found. Set NEXT_PUBLIC_OPENAI_API_KEY in .env.local');
        }
    }

    async sendMessage(
        messages: ChatMessage[],
        onThinking?: (isThinking: boolean) => void
    ): Promise<ChatCompletionResponse> {
        try {
            // Show thinking state
            onThinking?.(true);

            const response = await fetch(`${this.baseURL}/chat/completions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`,
                },
                body: JSON.stringify({
                    model: 'gpt-3.5-turbo',
                    messages: messages,
                    temperature: 0.7,
                    max_tokens: 1000,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.error?.message || `API error: ${response.status}`
                );
            }

            const data = await response.json();
            const assistantMessage = data.choices[0]?.message?.content || 'No response';

            return {
                message: assistantMessage,
            };
        } catch (error) {
            console.error('AI Service Error:', error);
            return {
                message: '',
                error: error instanceof Error ? error.message : 'Failed to get response',
            };
        } finally {
            // Hide thinking state
            onThinking?.(false);
        }
    }

    async streamMessage(
        messages: ChatMessage[],
        onChunk: (chunk: string) => void,
        onThinking?: (isThinking: boolean) => void
    ): Promise<void> {
        try {
            onThinking?.(true);

            const response = await fetch(`${this.baseURL}/chat/completions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`,
                },
                body: JSON.stringify({
                    model: 'gpt-3.5-turbo',
                    messages: messages,
                    temperature: 0.7,
                    max_tokens: 1000,
                    stream: true,
                }),
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();

            if (!reader) {
                throw new Error('No reader available');
            }

            onThinking?.(false);

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n').filter(line => line.trim() !== '');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') continue;

                        try {
                            const parsed = JSON.parse(data);
                            const content = parsed.choices[0]?.delta?.content;
                            if (content) {
                                onChunk(content);
                            }
                        } catch (e) {
                            // Skip invalid JSON
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Stream Error:', error);
            onThinking?.(false);
            throw error;
        }
    }
}

export const aiService = new AIService();
