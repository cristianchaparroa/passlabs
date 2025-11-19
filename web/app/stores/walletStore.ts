import { create } from 'zustand';

interface WalletState {
    isConnected: boolean;
    address: string | null;
    setConnected: (connected: boolean, address?: string) => void;
    disconnect: () => void;
}

export const useWalletStore = create<WalletState>((set) => ({
    isConnected: false,
    address: null,
    setConnected: (connected, address) =>
        set({ isConnected: connected, address: address || null }),
    disconnect: () =>
        set({ isConnected: false, address: null }),
}));