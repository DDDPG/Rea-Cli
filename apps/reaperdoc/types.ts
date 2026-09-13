export interface DocField {
  label: string;
  description: string;
  subFields?: string[];
  type?: string;
  index?: string;
  tags?: string[];
}

export interface DocEntry {
  name: string;
  description?: string;
  isChunk?: boolean;
  fields: DocField[];
  tags: string[];
  sourceFile?: string;
}

export interface InfoBlockItem {
  label: string;
  description: string;
}

export interface DocSection {
  id: string;
  title: string;
  subtitle: string;
  entries: DocEntry[];
  description?: string;
  introList?: {
    title: string;
    items: InfoBlockItem[];
  };
}

export interface RPPNode {
  key: string;
  values?: string;
  children?: RPPNode[];
  comment?: string;
  sectionId?: string; // Links to DocSection.id (project, track, item, etc.)
}