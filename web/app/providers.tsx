'use client';

import '@rainbow-me/rainbowkit/styles.css';
import { ReactNode } from 'react';
import {
    connectorsForWallets,
    RainbowKitProvider,
} from '@rainbow-me/rainbowkit';
import {
    metaMaskWallet,
    walletConnectWallet,
    injectedWallet,
} from '@rainbow-me/rainbowkit/wallets';
import { WagmiProvider, createConfig, http } from 'wagmi';
import {
    mainnet,
    polygon,
    optimism,
    arbitrum,
    base,
} from 'wagmi/chains';
import {
    QueryClientProvider,
    QueryClient,
} from "@tanstack/react-query";
import useWalletSync from "@/app/hooks/useWalletStore";

const connectors = connectorsForWallets(
    [
        {
            groupName: 'Recommended',
            wallets: [metaMaskWallet, walletConnectWallet, injectedWallet],
        },
    ],
    {
        appName: 'SwapPayAI',
        projectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID!,
    }
);

const config = createConfig({
    connectors,
    chains: [mainnet, polygon, optimism, arbitrum, base],
    ssr: true,
    transports: {
        [mainnet.id]: http(),
        [polygon.id]: http(),
        [optimism.id]: http(),
        [arbitrum.id]: http(),
        [base.id]: http(),
    },
});

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 1,
            refetchOnWindowFocus: false,
        },
    },
});

function WalletSyncProvider({ children }: { children: ReactNode }) {
    useWalletSync();
    return <>{children}</>;
}


export function Web3Providers({ children }: { children: ReactNode }) {

    return (
        <WagmiProvider config={config}>
            <QueryClientProvider client={queryClient}>
                <RainbowKitProvider
                    appInfo={{
                        appName: 'PassLabs',
                        learnMoreUrl: undefined,
                    }}
                >
                    <WalletSyncProvider>
                        {children}
                    </WalletSyncProvider>
                </RainbowKitProvider>
            </QueryClientProvider>
        </WagmiProvider>
    );
}