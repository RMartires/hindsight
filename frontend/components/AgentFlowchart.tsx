"use client";

import type { AgentStatus } from "@/lib/types";
import AgentNode from "./AgentNode";

interface Props {
  agents: Record<string, AgentStatus>;
  onNodeClick?: (agent: string) => void;
}

// Layout: positions for each agent node in the flowchart
// The pipeline: Analysts → Bull/Bear → Research Mgr → Trader → Risk team → Risk Judge
interface NodeDef {
  id: string;
  name: string;
  x: number;
  y: number;
}

interface EdgeDef {
  from: string;
  to: string;
}

const NODES: NodeDef[] = [
  // Analysts (column 1)
  { id: "Market Analyst", name: "Market", x: 80, y: 30 },
  { id: "Fundamentals Analyst", name: "Fundamentals", x: 80, y: 80 },
  { id: "News Analyst", name: "News", x: 80, y: 130 },
  { id: "Social Analyst", name: "Social", x: 80, y: 180 },

  // Research debate (column 2)
  { id: "Bull Researcher", name: "Bull", x: 250, y: 60 },
  { id: "Bear Researcher", name: "Bear", x: 250, y: 140 },

  // Research Manager (column 3)
  { id: "Research Manager", name: "Res. Manager", x: 410, y: 100 },

  // Trader (column 4)
  { id: "Trader", name: "Trader", x: 560, y: 100 },

  // Risk debate (column 5)
  { id: "Aggressive Analyst", name: "Aggressive", x: 710, y: 30 },
  { id: "Conservative Analyst", name: "Conservative", x: 710, y: 100 },
  { id: "Neutral Analyst", name: "Neutral", x: 710, y: 170 },

  // Risk Judge (column 6)
  { id: "Risk Judge", name: "Risk Judge", x: 870, y: 100 },
];

const EDGES: EdgeDef[] = [
  // Analysts → Bull/Bear
  { from: "Market Analyst", to: "Bull Researcher" },
  { from: "Fundamentals Analyst", to: "Bull Researcher" },
  { from: "News Analyst", to: "Bear Researcher" },
  { from: "Social Analyst", to: "Bear Researcher" },
  // Debate
  { from: "Bull Researcher", to: "Research Manager" },
  { from: "Bear Researcher", to: "Research Manager" },
  // Flow
  { from: "Research Manager", to: "Trader" },
  { from: "Trader", to: "Aggressive Analyst" },
  { from: "Trader", to: "Conservative Analyst" },
  { from: "Trader", to: "Neutral Analyst" },
  // Risk → Judge
  { from: "Aggressive Analyst", to: "Risk Judge" },
  { from: "Conservative Analyst", to: "Risk Judge" },
  { from: "Neutral Analyst", to: "Risk Judge" },
];

function getNodePos(id: string): { x: number; y: number } | undefined {
  return NODES.find((n) => n.id === id);
}

export default function AgentFlowchart({ agents, onNodeClick }: Props) {
  return (
    <div className="flowchart-container">
      <h3 className="section-title">Agent Pipeline</h3>
      <svg viewBox="0 0 950 210" className="flowchart-svg">
        <defs>
          <marker
            id="arrow"
            viewBox="0 0 10 6"
            refX="10"
            refY="3"
            markerWidth={8}
            markerHeight={6}
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 3 L 0 6 z" fill="#3f3f46" />
          </marker>
          <marker
            id="arrow-active"
            viewBox="0 0 10 6"
            refX="10"
            refY="3"
            markerWidth={8}
            markerHeight={6}
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 3 L 0 6 z" fill="#22c55e" />
          </marker>
        </defs>

        {/* Edges */}
        {EDGES.map((edge) => {
          const from = getNodePos(edge.from);
          const to = getNodePos(edge.to);
          if (!from || !to) return null;

          const fromStatus = agents[edge.from] || "pending";
          const isActive =
            fromStatus === "completed" || fromStatus === "in_progress";

          return (
            <line
              key={`${edge.from}-${edge.to}`}
              x1={from.x + 65}
              y1={from.y}
              x2={to.x - 65}
              y2={to.y}
              stroke={isActive ? "#22c55e40" : "#27272a"}
              strokeWidth={1.5}
              markerEnd={isActive ? "url(#arrow-active)" : "url(#arrow)"}
            />
          );
        })}

        {/* Nodes */}
        {NODES.map((node) => (
          <AgentNode
            key={node.id}
            name={node.name}
            status={agents[node.id] || "pending"}
            x={node.x}
            y={node.y}
            onClick={onNodeClick ? () => onNodeClick(node.id) : undefined}
          />
        ))}
      </svg>
    </div>
  );
}
