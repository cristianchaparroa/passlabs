'use client';

import { ConnectButton } from "@rainbow-me/rainbowkit";
import Link from "next/link";

const Navbar = () => {
    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-black/80 backdrop-blur-md border-b border-zinc-200 dark:border-zinc-800">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo/Brand */}
                    <Link href="/" className="text-xl font-bold text-zinc-900 dark:text-white">
                        PassLabs
                    </Link>

                    {/* Connect Button */}
                    <ConnectButton />
                </div>
            </div>
        </nav>
    );
};

export default Navbar;