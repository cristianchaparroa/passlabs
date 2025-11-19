'use client';

import Navbar from "@/app/components/navbar";
import {useWalletStore} from "@/app/stores/walletStore";

const Home = () => {
    const isConnected = useWalletStore((state) => state.isConnected);
    const address = useWalletStore((state) => state.address);

    return (
        <div className="min-h-screen">
            <Navbar />

            {/* Main content with padding to account for fixed navbar */}
            <main className="pt-16">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                    <div className="text-center">
                        <h1 className="text-4xl font-bold text-zinc-900 dark:text-white mb-4">
                            Welcome to PassLabs
                        </h1>

                        {!isConnected ? (
                            <p className="text-lg text-zinc-600 dark:text-zinc-400">
                                Connect your wallet to get started
                            </p>
                        ) : (
                            <div>
                                <p className="text-lg text-zinc-600 dark:text-zinc-400 mb-2">
                                    Welcome back!
                                </p>
                                <p className="text-sm text-zinc-500 dark:text-zinc-500">
                                    {address && `${address.slice(0, 6)}...${address.slice(-4)}`}
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Home;