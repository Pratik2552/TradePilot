import type { Metadata } from "next";
import ScannerPageClient from "./ScannerPageClient";

export const metadata: Metadata = { title: "Scanner" };

interface ScannerPageProps {
  params: Promise<{ id: string }>;
}

export default async function ScannerPage({ params }: ScannerPageProps) {
  const { id } = await params;
  return <ScannerPageClient strategyId={id} />;
}
