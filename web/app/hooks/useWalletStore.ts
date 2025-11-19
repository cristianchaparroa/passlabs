'use client';

import { useEffect } from 'react';
import { useAccount } from 'wagmi';
import {useWalletStore} from "@/app/stores/walletStore";

const useWalletSync = () =>  {
    const { address, isConnected } = useAccount();
    const setConnected = useWalletStore((state) => state.setConnected);

    useEffect(() => {
        setConnected(isConnected, address);
    }, [isConnected, address, setConnected]);
}

export default useWalletSync;