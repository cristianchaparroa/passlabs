'use client';

import Navbar from "@/app/components/navbar";
import { useRouter } from "next/navigation";

const Prices = () => {
    const router = useRouter();

    const handlePlanSelect = (planName: string) => {
        console.log(`Selected plan: ${planName}`);
        router.push('/chats');
    };
    const plans = [
        {
            name: "Free",
            price: 0,
            description: "See what AI can do",
            isCurrent: true,
            features: [
                "Get simple explanations",
                "Have short chats for common questions",
                "Try out image generation",
                "Save limited memory and context",
            ],
        },
        {
            name: "Plus",
            price: 20,
            description: "Unlock the full experience",
            isPopular: true,
            features: [
                "Solve complex problems",
                "Have long chats over multiple sessions",
                "Create more images, faster",
                "Remember goals and past conversations",
                "Plan travel and tasks with agent mode",
                "Organize projects and customize GPTs",
                "Produce and share videos on Sora",
                "Write code and build apps with Codex",
            ],
        },
        {
            name: "Pro",
            price: 200,
            description: "Maximize your productivity",
            features: [
                "Master advanced tasks and topics",
                "Tackle big projects with unlimited messages",
                "Create high-quality images at any scale",
                "Keep full context with maximum memory",
                "Run research and plan tasks with agents",
                "Scale your projects and automate workflows",
                "Expand your limits with Sora video creation",
                "Deploy code faster with Codex",
                "Get early access to experimental features",
            ],
        },
    ];

    return (
        <div className="min-h-screen bg-black">
            <Navbar />
            
            <main className="pt-24 pb-12 px-4">
                <div className="max-w-7xl mx-auto">
                    {/* Header */}
                    <h1 className="text-4xl font-bold text-white text-center mb-12">
                        Upgrade your plan
                    </h1>

                    {/* Pricing Cards */}
                    <div className="grid md:grid-cols-3 gap-6">
                        {plans.map((plan) => (
                            <div
                                key={plan.name}
                                className={`rounded-2xl p-8 ${
                                    plan.isPopular
                                        ? 'bg-gradient-to-b from-indigo-900/50 to-indigo-950/50 border-2 border-indigo-700'
                                        : 'bg-zinc-900 border border-zinc-800'
                                }`}
                            >
                                {/* Plan Header */}
                                <div className="mb-6">
                                    <div className="flex items-start justify-between mb-4">
                                        <h2 className="text-2xl font-bold text-white">
                                            {plan.name}
                                        </h2>
                                        {plan.isPopular && (
                                            <span className="px-3 py-1 rounded-full bg-indigo-600 text-white text-xs font-medium">
                                                POPULAR
                                            </span>
                                        )}
                                    </div>
                                    
                                    <div className="flex items-baseline mb-4">
                                        <span className="text-5xl font-bold text-white">
                                            ${plan.price}
                                        </span>
                                        <span className="ml-2 text-zinc-400">
                                            USD / month
                                        </span>
                                    </div>
                                    
                                    <p className="text-zinc-300 mb-6">
                                        {plan.description}
                                    </p>

                                    {/* CTA Button */}
                                    {plan.isCurrent ? (
                                        <button
                                            disabled
                                            className="w-full py-3 rounded-lg bg-zinc-800 text-zinc-500 font-medium cursor-not-allowed"
                                        >
                                            Your current plan
                                        </button>
                                    ) : (
                                        <button
                                            onClick={() => handlePlanSelect(plan.name)}
                                            className={`w-full py-3 rounded-lg font-medium transition-colors ${
                                                plan.isPopular
                                                    ? 'bg-indigo-600 hover:bg-indigo-700 text-white'
                                                    : 'bg-white hover:bg-zinc-100 text-black'
                                            }`}
                                        >
                                            Get {plan.name}
                                        </button>
                                    )}
                                </div>

                                {/* Features */}
                                <div className="space-y-4">
                                    {plan.features.map((feature, index) => (
                                        <div key={index} className="flex items-start gap-3">
                                            <div className="flex-shrink-0 w-5 h-5 rounded-full border border-zinc-600 flex items-center justify-center mt-0.5">
                                                <div className="w-2 h-2 rounded-full bg-zinc-400" />
                                            </div>
                                            <span className="text-zinc-300 text-sm">
                                                {feature}
                                            </span>
                                        </div>
                                    ))}
                                </div>

                                {/* Footer */}
                                {plan.name === "Free" && (
                                    <p className="mt-6 text-sm text-zinc-500">
                                        Have an existing plan?{" "}
                                        <a href="#" className="text-white underline">
                                            See billing help
                                        </a>
                                    </p>
                                )}
                                {plan.name === "Plus" && (
                                    <p className="mt-6 text-sm text-zinc-500">
                                        <a href="#" className="text-white underline">
                                            Limits apply
                                        </a>
                                    </p>
                                )}
                                {plan.name === "Pro" && (
                                    <p className="mt-6 text-sm text-zinc-500">
                                        Unlimited subject to abuse guardrails.{" "}
                                        <a href="#" className="text-white underline">
                                            Learn more
                                        </a>
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>

                    {/* Footer Icon */}
                    <div className="flex justify-center mt-12">
                        <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center">
                            <svg className="w-6 h-6 text-zinc-400" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                            </svg>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Prices;
