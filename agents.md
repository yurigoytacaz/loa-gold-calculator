# Ark Ledger — Calculadora de Gold de Lost Ark

Este documento descreve a arquitetura, stack tecnológica e regras de negócio do projeto **Ark Ledger**, uma calculadora e planejadora semanal de gold para o jogo Lost Ark.

---

## 🚀 Stack Tecnológica

O projeto foi construído utilizando tecnologias modernas e eficientes voltadas para a performance e execução inteiramente no lado do cliente (client-side):

1. **Svelte & SvelteKit (v5+)**:
   - Utiliza a versão mais recente do Svelte, adotando o sistema de **Runes** (`$state`, `$derived`) para reatividade fina e declarativa.
   - Eventos utilizando a nova sintaxe nativa (ex: `onclick` em vez de `on:click`).
   - Configurado com `@sveltejs/adapter-static` para gerar uma build estática (SPA/SSG), o que facilita o deploy em servidores estáticos comuns (como Apache, Nginx ou GitHub Pages).

2. **TypeScript**:
   - Tipagem estática em toda a aplicação para garantir a integridade dos dados (personagens, rosters, raids).

3. **Vite**:
   - Bundler ultra-rápido para desenvolvimento local e compilação do projeto.

4. **Vanilla CSS (CSS Puro)**:
   - Toda a identidade visual e grid responsiva estão definidos nos arquivos [app.css](file:///mnt/c/Users/Yuri/Documents/loa-gold-calculator/src/app.css) e [columns.css](file:///mnt/c/Users/Yuri/Documents/loa-gold-calculator/src/columns.css).
   - Utiliza fontes customizadas do Google Fonts (*Inter* e *DM Mono*) e variáveis CSS para cores e consistência de tema escuro.

5. **IndexedDB**:
   - Banco de dados no navegador usado para salvar os rosters e personagens localmente sem a necessidade de um backend dedicado. Gerenciado no arquivo [db.ts](file:///mnt/c/Users/Yuri/Documents/loa-gold-calculator/src/lib/db.ts).

---

## 📁 Estrutura de Arquivos Principal

* **[package.json](file:///mnt/c/Users/Yuri/Documents/loa-gold-calculator/package.json)**: Declaração de scripts e dependências do ecossistema SvelteKit + Vite.
* **[src/lib/db.ts](file:///mnt/c/Users/Yuri/Documents/loa-gold-calculator/src/lib/db.ts)**: Funções assíncronas para abrir a conexão, salvar, ler e deletar rosters usando o IndexedDB (`loadRosters`, `saveRoster`, `deleteRoster`).
* **[src/routes/+page.svelte](file:///mnt/c/Users/Yuri/Documents/loa-gold-calculator/src/routes/+page.svelte)**: O arquivo principal da calculadora contendo a interface do usuário (UI), formulários de criação e lógica reativa principal.
* **[src/app.css](file:///mnt/c/Users/Yuri/Documents/loa-gold-calculator/src/app.css)**: Estilos globais, painel de resumo, modal/drawer de gerenciamento de roster e layout responsivo.
* **[src/columns.css](file:///mnt/c/Users/Yuri/Documents/loa-gold-calculator/src/columns.css)**: Estilos específicos da tabela/grid que exibe as colunas de personagens ativos.

---

## ⚙️ Regras de Negócio e Funcionalidades

### 1. Limite de Personagens (Gold Earners)
* Conforme a mecânica de Lost Ark, apenas **6 personagens** por roster podem ganhar gold semanalmente.
* Os primeiros 6 personagens adicionados são definidos como **Earners** e são exibidos na grade principal de cálculo.
* A partir do 7º personagem, eles são classificados como **Reserves (Reservas)**. Eles aparecem no rodapé e não entram nos somatórios de gold semanal.

### 2. Seleção de Raids Semanais
* Cada personagem pode realizar e receber recompensa de no máximo **3 raids** por semana.
* Ao adicionar um novo personagem, o sistema faz uma **sugestão automática** das 3 melhores raids disponíveis para o Item Level (iLvl) inserido.
* **Validação de Nível**: Uma raid fica bloqueada (`locked`) se o item level do personagem for inferior ao exigido pela raid.
* **Validação de Chefe Único**: O sistema impede a seleção de múltiplas dificuldades do mesmo chefe na mesma semana (ex: Nightmare, Hard e Normal do "Padre" ou "Serka"). Se o usuário seleciona um modo de um chefe, qualquer outro modo selecionado anteriormente daquele mesmo chefe é desmarcado.

### 3. Distribuição e Cálculo de Gold
O cálculo do gold ganho varia conforme o chefe e a dificuldade selecionada:
* **Padre**: O gold obtido nesta raid é inteiramente vinculado ao personagem (*Character Bound*).
* **Raids Normais (exceto Padre)**: O gold é dividido igualmente (50/50) entre gold livre/comercializável (*Tradable/Free*) e gold vinculado ao roster (*Roster Bound*).
* **Raids Hard/Nightmare (exceto Padre)**: O gold é 100% livre/comercializável (*Tradable/Free*).

### 4. Painel de Resumos (Dashboard)
Apresenta a soma totalizada do gold planejado para a semana, dividido em quatro categorias:
1. **Character Bound**: Gold preso ao personagem.
2. **Roster Bound**: Gold preso ao roster (compartilhado na conta).
3. **Tradable/Free**: Gold livre e utilizável imediatamente.
4. **Gold Total**: A soma de todas as recompensas.

---

## 👥 Dados e Modelos

### Character (Personagem)
```typescript
export type Character = {
  id: string;
  nick: string;
  level: number;
  className: string;
  raids: string[]; // IDs das raids selecionadas
};
```

### Roster (Grupo de Personagens)
```typescript
export type Roster = {
  id: string;
  name: string;
  characters: Character[];
  createdAt: number;
};
```

### Raid (Chefe / Masmorra)
```typescript
type Raid = {
  id: string;
  boss: string;
  mode: string;
  level: number;
  gold: number;
  normal: boolean;
  padre: boolean;
};
```
