'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface PaymentToken {
    symbol: string;
    name: string;
    chain: string;
    icon: string;
    pricePerToken: number; // USD per token
}

interface PaymentModalProps {
    isOpen: boolean;
    onClose: () => void;
    planName: string;
    planPrice: number; // in USD
}

const paymentTokens: PaymentToken[] = [
    {
        symbol: 'ETH',
        name: 'Ethereum',
        chain: 'Mainnet',
        icon: 'https://cryptologos.cc/logos/ethereum-eth-logo.png',
        pricePerToken: 3500, // Example: 1 ETH = $3500
    },
    {
        symbol: 'ETH',
        name: 'Ethereum',
        chain: 'Scroll',
        icon: 'https://cryptologos.cc/logos/ethereum-eth-logo.png',
        pricePerToken: 3500,
    },
    {
        symbol: 'USDC',
        name: 'USD Coin',
        chain: 'Scroll',
        icon: 'https://cryptologos.cc/logos/usd-coin-usdc-logo.png',
        pricePerToken: 1, // 1 USDC = $1
    },
];

const PaymentModal = ({ isOpen, onClose, planName, planPrice }: PaymentModalProps) => {
    const [selectedToken, setSelectedToken] = useState<PaymentToken | null>(null);
    const router = useRouter();



    const calculateTokenAmount = (token: PaymentToken): string => {
        const tokenAmount = planPrice / token.pricePerToken;
        return tokenAmount.toFixed(6);
    };

    const handleBuy = () => {
        if (!selectedToken) return;
        console.log(`Buying ${planName} with ${calculateTokenAmount(selectedToken)} ${selectedToken.symbol} on ${selectedToken.chain}`);
        
        // Close modal and redirect to chats
        onClose();
        router.push('/chats');
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="bg-white dark:bg-zinc-900 rounded-2xl shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-bold text-zinc-900 dark:text-white">
                            Pay with Crypto
                        </h2>
                        <button
                            onClick={onClose}
                            className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200"
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                    <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-2">
                        {planName} Plan - ${planPrice} USD/month
                    </p>
                </div>

                {/* Payment Options */}
                <div className="p-6 space-y-3">
                    <p className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-4">
                        Select payment method:
                    </p>
                    {paymentTokens.map((token, index) => {
                        const tokenAmount = calculateTokenAmount(token);
                        const isSelected = selectedToken === token;
                        
                        return (
                            <button
                                key={index}
                                onClick={() => setSelectedToken(token)}
                                className={`w-full p-4 rounded-xl border-2 transition-all ${
                                    isSelected
                                        ? 'border-indigo-600 bg-indigo-50 dark:bg-indigo-950/30'
                                        : 'border-zinc-200 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700'
                                }`}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <img
                                            src={token.icon}
                                            alt={token.symbol}
                                            className="w-10 h-10 rounded-full"
                                        />
                                        <div className="text-left">
                                            <div className="font-semibold text-zinc-900 dark:text-white">
                                                {token.symbol} ({token.chain})
                                            </div>
                                            <div className="text-sm text-zinc-500 dark:text-zinc-400">
                                                {token.name}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="font-bold text-zinc-900 dark:text-white">
                                            ${planPrice}
                                        </div>
                                        <div className="text-sm text-zinc-600 dark:text-zinc-400">
                                            {tokenAmount} {token.symbol}
                                        </div>
                                    </div>
                                </div>
                            </button>
                        );
                    })}
                </div>

                {/* Action Buttons */}
                <div className="p-6 border-t border-zinc-200 dark:border-zinc-800 space-y-3">
                    <button
                        onClick={handleBuy}
                        disabled={!selectedToken}
                        className={`w-full py-3 rounded-xl font-medium transition-colors ${
                            selectedToken
                                ? 'bg-indigo-600 hover:bg-indigo-700 text-white'
                                : 'bg-zinc-200 dark:bg-zinc-800 text-zinc-400 cursor-not-allowed'
                        }`}
                    >
                        {selectedToken
                            ? `Pay ${calculateTokenAmount(selectedToken)} ${selectedToken.symbol}`
                            : 'Select a payment method'}
                    </button>
                    <button
                        onClick={onClose}
                        className="w-full py-3 rounded-xl font-medium text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PaymentModal;
