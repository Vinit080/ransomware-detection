"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Bug, FileBarChart2, Settings, ShieldAlert } from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Samples", href: "/samples", icon: Bug },
    { name: "Analytics", href: "/analytics", icon: FileBarChart2 },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <div className="w-64 h-full enterprise-panel border-y-0 border-l-0 rounded-none flex flex-col flex-shrink-0 z-20">
      <div className="p-6 flex flex-col items-center gap-3 border-b border-panel-border bg-[#0a0a0a]">
        <div className="p-3 bg-cyber-cyan/10 rounded border border-cyber-cyan/30">
          <ShieldAlert className="h-8 w-8 text-cyber-cyan" />
        </div>
        <h1 className="text-lg font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-cyber-cyan to-cyber-purple">
          RansomShield AI
        </h1>
      </div>
      
      <div className="flex flex-1 flex-col overflow-y-auto pt-6 px-4 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname.startsWith(item.href);
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all duration-200
                ${isActive 
                  ? "bg-cyber-cyan/10 text-cyber-cyan border border-cyber-cyan/30 shadow-[0_0_15px_rgba(6,182,212,0.15)]" 
                  : "text-gray-400 hover:text-white hover:bg-white/5"}
              `}
            >
              <item.icon className={`h-5 w-5 ${isActive ? "text-cyber-cyan" : ""}`} />
              {item.name}
            </Link>
          );
        })}
      </div>
      
      <div className="p-4 border-t border-panel-border">
        <div className="flex items-center gap-3 px-4 py-3 bg-black/40 rounded-lg border border-panel-border">
          <div className="h-2 w-2 rounded-full bg-cyber-cyan animate-pulse" />
          <span className="text-xs text-gray-400 font-mono tracking-wider">Engine: ACTIVE</span>
        </div>
      </div>
    </div>
  );
}
