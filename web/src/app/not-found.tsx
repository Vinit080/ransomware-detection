import Link from "next/link";
import { ShieldAlert, AlertTriangle } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center p-8 bg-background relative overflow-hidden">
      {/* Strict Grid Background for Enterprise Feel */}
      <div 
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(var(--panel-border) 1px, transparent 1px), linear-gradient(90deg, var(--panel-border) 1px, transparent 1px)`,
          backgroundSize: '40px 40px'
        }}
      />
      
      <div className="enterprise-panel max-w-lg w-full p-10 relative z-10 flex flex-col items-center text-center gap-8 border-alert-red/30 shadow-[0_0_50px_rgba(239,68,68,0.1)]">
        
        <div className="relative">
          <div className="absolute inset-0 bg-alert-red/20 blur-xl rounded-full animate-pulse" />
          <div className="relative p-6 bg-black border border-alert-red/30 rounded-full">
            <ShieldAlert className="h-16 w-16 text-alert-red" />
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <h1 className="text-4xl font-black tracking-widest text-white uppercase">
            Error 404
          </h1>
          <h2 className="text-xl font-bold tracking-widest text-alert-red uppercase flex items-center justify-center gap-2">
            <AlertTriangle className="h-5 w-5" /> Sector Not Found
          </h2>
        </div>

        <p className="text-gray-400 font-mono text-sm leading-relaxed border-y border-panel-border py-4 w-full">
          The requested system resource could not be located. Ensure you have the correct authorization clearance and URL trajectory before proceeding.
        </p>

        <Link 
          href="/dashboard"
          className="w-full py-4 rounded bg-cyber-cyan text-black font-bold uppercase tracking-widest hover:bg-white transition-colors text-sm shadow-[0_0_20px_rgba(6,182,212,0.4)]"
        >
          Return to Dashboard
        </Link>
      </div>
    </div>
  );
}
