import type { NewsItem } from "@/lib/api";

export default function NewsList({ items }: { items: NewsItem[] }) {
  if (items.length === 0) {
    return (
      <div className="crt-panel rounded-lg p-5">
        <h2 className="mb-2 text-sm tracking-widest text-matrixDim">NEWS</h2>
        <p className="text-sm text-matrixDim/70">
          No recent headlines found, or the news provider isn&apos;t configured yet.
        </p>
      </div>
    );
  }

  return (
    <div className="crt-panel rounded-lg p-5">
      <h2 className="mb-3 text-sm tracking-widest text-matrixDim">NEWS</h2>
      <ul className="space-y-3">
        {items.map((item, i) => (
          <li key={i} className="border-b border-panelBorder pb-3 last:border-0 last:pb-0">
            <a href={item.url} target="_blank" rel="noreferrer" className="text-sm font-medium hover:text-matrix hover:glow-text hover:underline">
              {item.title}
            </a>
            <p className="mt-1 text-xs text-matrixDim/70">
              {item.source} · {new Date(item.published_at).toLocaleDateString("en-IN")}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
