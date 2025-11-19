import { Web3Providers } from './providers';
import Home from "@/app/pages/home"

export default function App() {
    return (
        <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
            <Web3Providers>
                <Home/>
            </Web3Providers>
        </div>
    );
}