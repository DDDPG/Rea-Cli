import React, { useState, useMemo, useEffect, useRef } from 'react';
import { 
  Search, 
  Menu, 
  X, 
  ChevronDown, 
  ChevronRight, 
  Copy, 
  FileCode, 
  Layers, 
  Music, 
  Sliders, 
  Zap, 
  Filter, 
  Info, 
  CheckCircle2, 
  Disc, 
  Piano, 
  FileJson, 
  BookOpen, 
  Code2, 
  Activity 
} from 'lucide-react';
import { DOC_DATA } from './constants';
import { RPP_STRUCTURE } from './rppStructure';
import { DocEntry, DocSection, RPPNode, InfoBlockItem } from './types';

// --- Components ---

const HighlightText: React.FC<{ text: string | undefined, highlight: string }> = ({ text, highlight }) => {
  if (!text) return null;
  if (!highlight || !highlight.trim()) return <>{text}</>;
  
  const regex = new RegExp(`(${highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  const parts = text.split(regex);
  
  return (
    <span>
      {parts.map((part, i) => 
        regex.test(part) ? <span key={i} className="bg-reaper-warn/20 text-reaper-warn font-bold rounded-sm px-0.5">{part}</span> : part
      )}
    </span>
  );
};

const Badge: React.FC<{ type: string; highlight?: string }> = ({ type, highlight }) => {
  const colors: Record<string, string> = {
    'string': 'bg-blue-900/40 text-blue-300 border-blue-800',
    'int': 'bg-purple-900/40 text-purple-300 border-purple-800',
    'float': 'bg-teal-900/40 text-teal-300 border-teal-800',
    'bool': 'bg-indigo-900/40 text-indigo-300 border-indigo-800',
    'GUID': 'bg-orange-900/40 text-orange-300 border-orange-800',
    'chunk': 'bg-gray-700 text-gray-300 border-gray-600',
    'TODO': 'bg-yellow-900/20 text-yellow-500 border-yellow-700/50',
    'NOT CLEAR': 'bg-red-900/20 text-red-400 border-red-800/50',
    'AUDIO': 'bg-emerald-900/40 text-emerald-300 border-emerald-800',
    'MIDI': 'bg-amber-900/40 text-amber-300 border-amber-800',
    'DEPRECATED': 'bg-stone-800 text-stone-500 border-stone-700 line-through',
    'INFO': 'bg-cyan-900/40 text-cyan-300 border-cyan-800',
  };

  const defaultColor = 'bg-gray-800 text-gray-400 border-gray-700';
  const style = colors[type] || (type.includes('int') ? colors['int'] : (type.includes('bool') ? colors['bool'] : defaultColor));

  return (
    <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded border ${style} tracking-wider`}>
      {highlight ? <HighlightText text={type} highlight={highlight} /> : type}
    </span>
  );
};

const SectionIcon = ({ id }: { id: string }) => {
  switch (id) {
    case 'entry-point': return <FileCode size={18} />;
    case 'project': return <Layers size={18} />;
    case 'track': return <Music size={18} />;
    case 'item': return <Zap size={18} />;
    case 'take': return <Disc size={18} />;
    case 'source': return <Piano size={18} />;
    case 'fx': return <Sliders size={18} />;
    case 'envelope': return <Activity size={18} />;
    default: return <FileCode size={18} />;
  }
};

const SubFields: React.FC<{ items: string[]; highlight?: string }> = ({ items, highlight }) => {
  const [copiedVal, setCopiedVal] = useState<string | null>(null);

  const parseItem = (item: string) => {
    // Regex matches "Value = Desc", "Value - Desc", "+Value = Desc", "Value: Desc"
    // Also handles "1 = normal" or "+2 = enable..." or "0-15 = Desc"
    const match = item.match(/^([+-]?[\w\d\&\.]+(?:-[\w\d\.]+)?)[\s]*(?:=|:|-)(?:[\s]*)(.*)$/);
    if (match) {
      return { 
        val: match[1], 
        desc: match[2].replace(/^['"](.*)['"]$/, '$1'), // remove quotes if present
        isFlag: match[1].startsWith('+') || match[1].startsWith('-') 
      };
    }
    
    // Fallback for just notes
    return { val: null, desc: item, isFlag: false };
  };

  const parsedItems = items.map(parseItem);
  const mappings = parsedItems.filter(i => i.val !== null);
  const notes = parsedItems.filter(i => i.val === null);

  const handleCopy = (e: React.MouseEvent, val: string) => {
    e.stopPropagation();
    navigator.clipboard.writeText(val);
    setCopiedVal(val);
    setTimeout(() => setCopiedVal(null), 1500);
  };

  return (
    <div className="mt-3 text-xs animate-in fade-in duration-300">
      {mappings.length > 0 && (
        <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 bg-black/20 p-3 rounded border border-gray-800/50">
          <div className="col-span-2 text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">
             Values & Flags
          </div>
          {mappings.map((m, i) => (
            <React.Fragment key={i}>
              <div 
                className={`font-mono font-bold text-right cursor-pointer group flex items-center justify-end gap-2 ${m.isFlag ? 'text-reaper-secondary' : 'text-reaper-accent'}`}
                onClick={(e) => m.val && handleCopy(e, m.val)}
                title="Click to copy value"
              >
                <span className="opacity-0 group-hover:opacity-100 transition-opacity">
                  {copiedVal === m.val ? <CheckCircle2 size={10} /> : <Copy size={10} />}
                </span>
                <span className="group-hover:underline decoration-dotted underline-offset-4 whitespace-nowrap">
                   {highlight ? <HighlightText text={m.val!} highlight={highlight} /> : m.val}
                </span>
              </div>
              <div className="text-gray-300 leading-relaxed py-0.5">
                {highlight ? <HighlightText text={m.desc} highlight={highlight} /> : m.desc}
              </div>
            </React.Fragment>
          ))}
        </div>
      )}
      {notes.length > 0 && (
        <div className={`flex flex-col gap-2 ${mappings.length > 0 ? 'mt-3 pt-2 border-t border-gray-800/30' : ''}`}>
          {notes.map((n, i) => (
            <div key={i} className="flex gap-2 text-gray-500 italic px-2">
              <span className="opacity-50 text-reaper-warn">•</span>
              <span>{highlight ? <HighlightText text={n.desc} highlight={highlight} /> : n.desc}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const IntroBlock: React.FC<{ title: string; items: InfoBlockItem[] }> = ({ title, items }) => {
  return (
    <div className="mb-8 rounded-lg border border-gray-700 bg-gray-900/50 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700 bg-gray-800/50 flex items-center gap-2">
        <Info size={16} className="text-reaper-secondary" />
        <h4 className="font-bold text-sm text-gray-200 uppercase tracking-wide">{title}</h4>
      </div>
      <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {items.map((item, idx) => (
          <div key={idx} className="text-sm">
            <div className="font-mono font-bold text-reaper-accent mb-1">{item.label}</div>
            <div className="text-gray-400 text-xs leading-relaxed">{item.description}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

const EntryCard: React.FC<{ entry: DocEntry; showTodos: boolean; highlight?: boolean; onHighlightEnd?: () => void; searchQuery?: string }> = ({ entry, showTodos, highlight, onHighlightEnd, searchQuery }) => {
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (highlight) {
      if (cardRef.current) {
         cardRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
         // Optional: temporary highlight animation
         const timer = setTimeout(() => {
            onHighlightEnd && onHighlightEnd();
         }, 2000);
         return () => clearTimeout(timer);
      }
    }
  }, [highlight, onHighlightEnd]);

  if (!showTodos && (entry.tags.includes('TODO') || entry.tags.includes('NOT CLEAR'))) return null;

  const copyToClipboard = (e: React.MouseEvent, text: string) => {
    e.stopPropagation();
    navigator.clipboard.writeText(text);
  };

  return (
    <div 
      ref={cardRef}
      className={`mb-4 border rounded-lg transition-all duration-300 ${highlight ? 'ring-2 ring-reaper-accent shadow-[0_0_20px_rgba(0,179,134,0.2)]' : ''} bg-reaper-panel/40 border-gray-800`}
    >
      <div 
        className="flex items-start justify-between p-4"
      >
        <div className="flex items-start gap-3 overflow-hidden">
          <div className={`mt-1 p-1.5 rounded-md transition-colors ${entry.isChunk ? 'bg-indigo-500/10 text-indigo-400' : 'bg-reaper-accent/10 text-reaper-accent'}`}>
            {entry.isChunk ? <Layers size={16} /> : <Zap size={16} />}
          </div>
          <div className="flex flex-col min-w-0">
            <h3 className="font-mono font-bold text-lg truncate flex items-center gap-2 text-gray-100 flex-wrap">
              {searchQuery ? <HighlightText text={entry.name} highlight={searchQuery} /> : entry.name}
              {entry.tags.map(t => <Badge key={t} type={t} highlight={searchQuery} />)}
            </h3>
            {entry.description && <p className="text-sm text-gray-500 mt-1">
              {searchQuery ? <HighlightText text={entry.description} highlight={searchQuery} /> : entry.description}
            </p>}
          </div>
        </div>
        <div className="flex items-center gap-2 opacity-100 transition-opacity">
           <button 
             onClick={(e) => copyToClipboard(e, entry.name)}
             className="p-1.5 hover:bg-white/10 rounded-md text-gray-400 hover:text-white transition-colors"
             title="Copy Name"
           >
             <Copy size={14} />
           </button>
        </div>
      </div>

      <div className="px-4 pb-4">
        <div className="pt-0 border-t border-gray-700/50">
           <div className="mt-4 space-y-4">
             {entry.fields.map((field, idx) => (
               <div key={idx} className="relative pl-4 border-l-2 border-gray-700 hover:border-reaper-accent transition-colors py-1 group/field">
                 <div className="flex items-baseline gap-2 mb-1 flex-wrap">
                   <span className="text-xs font-mono text-reaper-secondary bg-blue-900/20 px-1.5 py-0.5 rounded border border-blue-900/30">
                     {searchQuery ? <HighlightText text={field.label} highlight={searchQuery} /> : field.label}
                   </span>
                   {field.type && <Badge type={field.type} highlight={searchQuery} />}
                   {field.tags && field.tags.map(t => <Badge key={t} type={t} highlight={searchQuery} />)}
                 </div>
                 <p className="text-gray-300 text-sm leading-relaxed">
                   {searchQuery ? <HighlightText text={field.description} highlight={searchQuery} /> : field.description}
                 </p>
                 {field.subFields && field.subFields.length > 0 && (
                   <SubFields items={field.subFields} highlight={searchQuery} />
                 )}
               </div>
             ))}
           </div>
           {entry.sourceFile && (
             <div className="mt-4 pt-3 border-t border-gray-800 text-xs text-gray-600 font-mono flex items-center gap-1 justify-end">
               <Info size={12} />
               Source: {entry.sourceFile}
             </div>
           )}
        </div>
      </div>
    </div>
  );
};

// --- RPP Viewer Component ---
const RPPNodeViewer: React.FC<{ 
  node: RPPNode; 
  depth: number; 
  onNavigate: (key: string, context: string) => void;
  documentedKeys: Set<string>;
  lastChild?: boolean;
}> = ({ node, depth, onNavigate, documentedKeys, lastChild }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const hasChildren = node.children && node.children.length > 0;
  
  // Format matching the RPP style
  const isChunk = node.key.startsWith('<');
  
  // Check if documented
  const cleanKey = node.key.replace(/[<>]/g, '');
  const isDocumented = documentedKeys.has(cleanKey);

  // Styling based on documentation status
  const keyColorClass = isChunk
    ? (isDocumented ? 'text-indigo-400' : 'text-red-400')
    : (isDocumented ? 'text-reaper-accent' : 'text-red-400');
  
  const handleKeyClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    // Allow navigation if explicit section exists, even if exact key isn't "documented"
    // This allows clicking generic envelopes (PANENV) to go to "envelope" section
    if (node.sectionId) {
      onNavigate(cleanKey, node.sectionId);
    }
  };

  const toggleCollapse = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsCollapsed(!isCollapsed);
  };

  return (
    <div className="font-mono text-sm leading-relaxed whitespace-nowrap">
      <div 
        className={`flex items-start hover:bg-white/5 transition-colors rounded-sm px-1 -mx-1`}
        style={{ paddingLeft: `${depth * 1.5}rem` }}
        onClick={hasChildren ? toggleCollapse : undefined}
      >
        {/* Toggle Icon or Spacer */}
        <span className="w-5 flex-shrink-0 text-gray-500 flex items-center justify-center cursor-pointer">
          {hasChildren && (
            <button onClick={toggleCollapse} className="hover:text-white">
              {isCollapsed ? <ChevronRight size={14} /> : <ChevronDown size={14} />}
            </button>
          )}
        </span>

        <div className="flex-1 flex gap-3">
          {/* Key */}
          <span 
            className={`${keyColorClass} font-bold ${node.sectionId ? 'hover:underline decoration-dotted cursor-pointer' : 'cursor-default opacity-80'}`}
            onClick={handleKeyClick}
            title={node.sectionId ? `Go to definition` : "Definition not found in API Reference"}
          >
            {node.key}
          </span>
          
          {/* Values */}
          {node.values && (
            <span className="text-gray-300 truncate max-w-md">{node.values}</span>
          )}

          {/* Comment */}
          {node.comment && (
            <span className="text-gray-600 italic">// {node.comment}</span>
          )}
          
          {/* Collapsed Indicator */}
          {isCollapsed && hasChildren && (
             <span className="text-gray-600 bg-gray-800 px-1 rounded text-xs self-center">... &gt;</span>
          )}
        </div>
      </div>

      {/* Recursive Children */}
      {hasChildren && !isCollapsed && (
        <div className="relative">
           {/* Indentation Guide Line */}
           <div 
             className="absolute border-l border-gray-800 h-full" 
             style={{ left: `${(depth * 1.5) + 0.6}rem`, top: 0 }} 
           />
           {node.children!.map((child, idx) => (
             <RPPNodeViewer 
               key={idx} 
               node={child} 
               depth={depth + 1} 
               onNavigate={onNavigate}
               documentedKeys={documentedKeys}
               lastChild={idx === node.children!.length - 1}
             />
           ))}
           {/* Closing Tag for Chunks */}
           {isChunk && (
             <div 
               className="text-indigo-400/50 hover:text-indigo-400 pl-7"
               style={{ paddingLeft: `${(depth * 1.5) + 1.25}rem` }}
             >
               &gt;
             </div>
           )}
        </div>
      )}
    </div>
  );
};

export default function App() {
  const [activeTab, setActiveTab] = useState<'docs' | 'structure'>('structure');
  const [activeSection, setActiveSection] = useState(DOC_DATA[0].id);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [showTodos, setShowTodos] = useState(true);
  const [highlightedParam, setHighlightedParam] = useState<string | null>(null);

  // Calculate documented keys for lookup
  const documentedKeys = useMemo(() => {
    const keys = new Set<string>();
    DOC_DATA.forEach(section => {
      section.entries.forEach(entry => {
        // Handle split names like "e/E" or "VOLENV / PANENV"
        const parts = entry.name.split('/');
        parts.forEach(p => {
          const clean = p.trim().replace(/[<>]/g, '');
          keys.add(clean);
        });
      });
      // Also check introList
      if (section.introList) {
        section.introList.items.forEach(item => {
           keys.add(item.label);
        });
      }
    });
    return keys;
  }, []);

  const filteredSections = useMemo(() => {
    if (!searchQuery) return DOC_DATA;
    
    return DOC_DATA.map(section => {
      const lowerQuery = searchQuery.toLowerCase();
      // Filter entries deeply
      const entries = section.entries.filter(e => {
        const matchesName = e.name.toLowerCase().includes(lowerQuery);
        const matchesDesc = e.description?.toLowerCase().includes(lowerQuery);
        const matchesTags = e.tags.some(t => t.toLowerCase().includes(lowerQuery));
        const matchesFields = e.fields.some(f => 
             f.label.toLowerCase().includes(lowerQuery) || 
             f.description.toLowerCase().includes(lowerQuery) ||
             (f.type && f.type.toLowerCase().includes(lowerQuery)) ||
             f.subFields?.some(sf => sf.toLowerCase().includes(lowerQuery))
        );
        return matchesName || matchesDesc || matchesTags || matchesFields;
      });

      if (entries.length > 0 || (section.introList && searchQuery.toLowerCase().includes('envelope'))) {
         return { ...section, entries };
      }
      return null;
    }).filter(Boolean) as DocSection[];
  }, [searchQuery]);

  const scrollToSection = (id: string) => {
    // Clear specific param highlight when navigating via sidebar to prevent jumping
    setHighlightedParam(null);
    setActiveSection(id);
    setMobileMenuOpen(false);
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  const handleStructureNavigation = (key: string, contextId: string) => {
    setActiveTab('docs');
    setActiveSection(contextId);
    
    // Check if exact key exists or if we should just go to the section
    // If it's an envelope type (e.g. PANENV), and we have a generic entry for it, try to find match
    const exists = documentedKeys.has(key);
    
    // For envelopes, try to find the "Envelope Types" block if exact match fails
    if (contextId === 'envelope' && !exists) {
       setHighlightedParam(null); 
       // Only scroll to section if we don't have a specific param to highlight
       setTimeout(() => {
         const el = document.getElementById(contextId);
         if (el) el.scrollIntoView({ behavior: 'smooth' });
       }, 50);
    } else {
       // Set highlight, let EntryCard handle the scrolling via its useEffect
       // IMPORTANT: Do NOT call scrollToSection here, as it conflicts with EntryCard scroll
       setHighlightedParam(key);
    }
  };

  const formatSidebarTitle = (title: string) => {
    const cleaned = title.replace(/[<>]/g, '').replace(/_/g, ' ').trim();
    if (!cleaned) return title;
    return cleaned.charAt(0).toUpperCase() + cleaned.slice(1).toLowerCase();
  };

  return (
    <div className="flex h-screen overflow-hidden bg-reaper-dark text-gray-200">
      
      {/* Sidebar - Desktop */}
      <aside className="hidden md:flex flex-col w-72 border-r border-gray-800 bg-[#181818] flex-shrink-0">
        <div className="p-6 border-b border-gray-800 flex items-center gap-3">
          <div className="w-8 h-8 bg-reaper-accent rounded flex items-center justify-center text-black font-bold text-xl shadow-[0_0_15px_rgba(0,179,134,0.3)]">
            R
          </div>
          <div>
            <h1 className="font-bold tracking-tight text-white">Reaper Parser</h1>
            <p className="text-xs text-gray-500 font-mono">v1.1.0 Ref</p>
          </div>
        </div>
        
        {activeTab === 'docs' && (
          <div className="p-4 animate-in fade-in slide-in-from-left-4 duration-300">
            <div className="relative group">
              <Search className="absolute left-3 top-2.5 text-gray-500 group-focus-within:text-reaper-accent transition-colors" size={16} />
              <input 
                type="text" 
                placeholder="Search anything (names, tags, fields)..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-reaper-panel border border-gray-700 rounded-lg py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-reaper-accent focus:ring-1 focus:ring-reaper-accent transition-all placeholder-gray-600"
              />
            </div>
          </div>
        )}

        <nav className="flex-1 overflow-y-auto px-4 pb-6 space-y-1 custom-scrollbar">
          {activeTab === 'docs' ? (
             DOC_DATA.map(section => (
              <button
                key={section.id}
                onClick={() => scrollToSection(section.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-all duration-200 group ${activeSection === section.id ? 'bg-reaper-accent text-black font-semibold shadow-md' : 'text-gray-400 hover:bg-white/5 hover:text-white'}`}
              >
                <span className={activeSection === section.id ? 'text-black' : 'text-gray-500 group-hover:text-gray-300'}>
                  <SectionIcon id={section.id} />
                </span>
                {formatSidebarTitle(section.title)}
              </button>
            ))
          ) : (
            <div className="text-sm text-gray-500 p-4 italic text-center">
              Navigate the project tree on the right to jump to definitions.
            </div>
          )}
        </nav>

        <div className="p-4 border-t border-gray-800 text-xs text-gray-600 text-center">
          Parser API Reference
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full relative">
        
        {/* Mobile Header */}
        <header className="md:hidden flex items-center justify-between p-4 border-b border-gray-800 bg-[#181818] z-20 sticky top-0">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-reaper-accent rounded flex items-center justify-center text-black font-bold text-sm">R</div>
            <span className="font-bold">Reaper Parser</span>
          </div>
          <button onClick={() => setMobileMenuOpen(true)} className="p-2 text-gray-400">
            <Menu size={24} />
          </button>
        </header>

        {/* Tab Switcher (Top Bar) */}
        <div className="flex border-b border-gray-800 bg-[#181818]">
          <button 
            onClick={() => setActiveTab('structure')}
            className={`flex-1 md:flex-none md:w-48 py-3 text-sm font-medium flex items-center justify-center gap-2 border-b-2 transition-colors ${activeTab === 'structure' ? 'border-reaper-accent text-white bg-white/5' : 'border-transparent text-gray-400 hover:text-white hover:bg-white/5'}`}
          >
            <Code2 size={16} />
            Project Structure
          </button>
          <button 
            onClick={() => setActiveTab('docs')}
            className={`flex-1 md:flex-none md:w-48 py-3 text-sm font-medium flex items-center justify-center gap-2 border-b-2 transition-colors ${activeTab === 'docs' ? 'border-reaper-accent text-white bg-white/5' : 'border-transparent text-gray-400 hover:text-white hover:bg-white/5'}`}
          >
            <BookOpen size={16} />
            API Reference
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden relative">
          
          {/* View: DOCS */}
          {activeTab === 'docs' && (
            <div className="h-full overflow-y-auto custom-scrollbar p-4 md:p-8 lg:px-12 max-w-7xl mx-auto w-full relative animate-in fade-in zoom-in-95 duration-200">
               {/* Controls Bar */}
              <div className="sticky top-0 z-10 mb-8 -mx-4 px-4 py-3 bg-reaper-dark/95 backdrop-blur border-b border-gray-800 flex justify-between items-center shadow-lg">
                 <div className="text-sm text-gray-400 hidden sm:block">
                   Showing <span className="text-white font-mono">{filteredSections.reduce((acc, s) => acc + s.entries.length, 0)}</span> parameters
                 </div>
                 
                 <button 
                   onClick={() => setShowTodos(!showTodos)}
                   className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium border transition-colors ${showTodos ? 'bg-reaper-panel text-reaper-accent border-reaper-accent' : 'bg-transparent text-gray-500 border-gray-700 hover:border-gray-500'}`}
                 >
                   <Filter size={12} />
                   {showTodos ? 'Hide TODOs' : 'Show TODOs'}
                 </button>
              </div>

              {filteredSections.map(section => (
                <div key={section.id} id={section.id} className="mb-16 scroll-mt-24">
                  <div className="mb-6 pb-4 border-b border-gray-800">
                    <h2 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                      <span className="text-reaper-accent opacity-50"><SectionIcon id={section.id} /></span>
                      {section.title}
                    </h2>
                    <div className="flex items-center gap-4 mt-2">
                       <h3 className="text-reaper-secondary font-mono text-sm uppercase tracking-wider font-semibold">{section.subtitle}</h3>
                       {section.description && <span className="text-gray-600 text-sm">• {section.description}</span>}
                    </div>
                  </div>
                  
                  {section.introList && (
                    <IntroBlock title={section.introList.title} items={section.introList.items} />
                  )}

                  <div className="grid grid-cols-1 gap-4">
                    {section.entries.map((entry, idx) => (
                      <EntryCard 
                        key={idx} 
                        entry={entry} 
                        showTodos={showTodos} 
                        searchQuery={searchQuery}
                        highlight={
                          !!highlightedParam && (
                            highlightedParam === entry.name || 
                            highlightedParam === entry.name.replace(/[<>]/g, '') || 
                            (entry.name.includes('/') && entry.name.includes(highlightedParam))
                          )
                        }
                        onHighlightEnd={() => setHighlightedParam(null)}
                      />
                    ))}
                  </div>

                  {section.entries.filter(e => !showTodos && (e.tags.includes('TODO') || e.tags.includes('NOT CLEAR'))).length > 0 && (
                     <div className="mt-4 text-center text-xs text-gray-600 italic">
                       {section.entries.filter(e => e.tags.includes('TODO') || e.tags.includes('NOT CLEAR')).length} hidden TODO/Unclear items
                     </div>
                  )}
                </div>
              ))}

              <footer className="mt-20 pt-10 border-t border-gray-800 text-center text-gray-600 text-sm mb-10">
                <p>Generated from source code annotations.</p>
                <p className="mt-2 text-xs font-mono">.RPP Parser API Reference</p>
              </footer>
            </div>
          )}

          {/* View: STRUCTURE */}
          {activeTab === 'structure' && (
            <div className="h-full overflow-y-auto custom-scrollbar p-4 md:p-8 animate-in fade-in zoom-in-95 duration-200 bg-[#1e1e1e]">
              <div className="max-w-4xl mx-auto">
                <div className="mb-6 p-4 bg-blue-900/20 border border-blue-900/50 rounded-lg text-sm text-blue-200 flex items-start gap-3">
                  <Info className="flex-shrink-0 mt-0.5" size={18} />
                  <div>
                    <h4 className="font-bold mb-1">Interactive Project Map</h4>
                    <p>This is a visualization of the sample .RPP project structure. Click on any <span className="text-reaper-accent font-mono font-bold">highlighted tag</span> to jump directly to its definition. Items in <span className="text-red-400 font-mono font-bold">red</span> are currently undocumented.</p>
                  </div>
                </div>

                <div className="font-mono bg-[#181818] p-6 rounded-lg border border-gray-800 shadow-xl overflow-x-auto">
                   <RPPNodeViewer 
                      node={RPP_STRUCTURE} 
                      depth={0} 
                      onNavigate={handleStructureNavigation} 
                      documentedKeys={documentedKeys}
                   />
                </div>
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}