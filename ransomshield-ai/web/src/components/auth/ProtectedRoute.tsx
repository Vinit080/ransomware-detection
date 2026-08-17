"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/store/useAuthStore";
import { ShieldAlert, Loader2 } from "lucide-react";

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Small delay to prevent layout shift flash during hydration
    const timer = setTimeout(() => {
      if (!isAuthenticated && pathname !== "/login") {
        router.push("/login");
      } else {
        setIsChecking(false);
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [isAuthenticated, pathname, router]);

  if (isChecking || !isAuthenticated) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center bg-background text-cyber-cyan gap-4">
        <ShieldAlert className="h-12 w-12 animate-pulse" />
        <Loader2 className="h-6 w-6 animate-spin" />
        <p className="font-mono text-sm tracking-widest uppercase text-gray-500 mt-2">Verifying Credentials...</p>
      </div>
    );
  }

  return <>{children}</>;
}
