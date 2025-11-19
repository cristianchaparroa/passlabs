'use client';

import Navbar from "@/app/components/navbar";

const Chats = () => {
    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-black">
            <Navbar />
            
            <main className="pt-24 pb-12 px-4">
                <div className="max-w-7xl mx-auto">
                    <h1 className="text-4xl font-bold text-zinc-900 dark:text-white">
                        Chats
                    </h1>
                </div>
            </main>
        </div>
    );
};

export default Chats;
