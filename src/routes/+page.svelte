<script lang="ts">
  import { onMount } from 'svelte';
  import { BibleApiService, type BibleRegion, type BibleRosterCharacter } from '$lib/BibleApiService';
  import { deleteRoster, loadRosters, saveRoster, type Character, type Roster } from '$lib/db';

  type Raid = { id: string; boss: string; mode: string; level: number; gold: number; normal: boolean; padre: boolean };
  const raids: Raid[] = [
    { id: 'padre-nm', boss: 'Padre', mode: 'Nightmare', level: 1750, gold: 50000, normal: false, padre: true },
    { id: 'padre-hm', boss: 'Padre', mode: 'Hard', level: 1720, gold: 40000, normal: false, padre: true },
    { id: 'padre-normal', boss: 'Padre', mode: 'Normal', level: 1700, gold: 30000, normal: true, padre: true },
    { id: 'kazeros-hm', boss: 'Kazeros', mode: 'Hard', level: 1730, gold: 52000, normal: false, padre: false },
    { id: 'kazeros-normal', boss: 'Kazeros', mode: 'Normal', level: 1710, gold: 40000, normal: true, padre: false },
    { id: 'serka-nm', boss: 'Serka', mode: 'Nightmare', level: 1740, gold: 54000, normal: false, padre: false },
    { id: 'serka-hm', boss: 'Serka', mode: 'Hard', level: 1730, gold: 44000, normal: false, padre: false },
    { id: 'serka-normal', boss: 'Serka', mode: 'Normal', level: 1710, gold: 35000, normal: true, padre: false },
    { id: 'armoche-hm', boss: 'Armoche', mode: 'Hard', level: 1720, gold: 42000, normal: false, padre: false },
    { id: 'armoche-normal', boss: 'Armoche', mode: 'Normal', level: 1700, gold: 33000, normal: true, padre: false }
  ];
  const classes = ['Aeromancer', 'Arcanist', 'Artist', 'Artillerist', 'Bard', 'Berserker', 'Breaker', 'Deadeye', 'Deathblade', 'Destroyer', 'Glaivier', 'Guardianknight', 'Gunslinger', 'Gunlancer', 'Machinist', 'Paladin', 'Reaper', 'Scrapper', 'Shadowhunter', 'Sharpshooter', 'Slayer', 'Sorceress', 'Souleater', 'Soulfist', 'Striker', 'Summoner', 'Valkyrie', 'Wardancer', 'Wildsoul'];
  const raidBosses = ['Padre', 'Serka', 'Kazeros', 'Armoche'];
  const modeRank: Record<string, number> = { Nightmare: 3, Hard: 2, Normal: 1 };

  let rosters = $state<Roster[]>([]);
  let activeId = $state('');
  let newRosterName = $state('');
  let showRosterForm = $state(false);
  let showCharacterForm = $state(false);
  let menuOpen = $state(false);
  let rosterDrawerOpen = $state(false);
  let showRenameRoster = $state(false);
  let renameRosterName = $state('');
  let draft = $state<{ nick: string; level: number | undefined; className: string }>({ nick: '', level: undefined, className: '' });
  let importDraft = $state<{ characterName: string; region: BibleRegion }>({ characterName: '', region: 'NA' });
  let importLoading = $state(false);
  let importError = $state('');
  let importMessage = $state('');
  let loaded = $state(false);
  let confirmCharacterId = $state<string | null>(null);
  let active = $derived(rosters.find((r) => r.id === activeId));
  let earners = $derived(active?.characters.slice(0, 6) ?? []);
  let reserves = $derived(active?.characters.slice(6) ?? []);

  onMount(async () => {
    rosters = await loadRosters();
    if (!rosters.length) {
      const starter: Roster = { id: crypto.randomUUID(), name: 'Meu roster', createdAt: Date.now(), characters: [] };
      rosters = [starter]; await saveRoster(starter);
    }
    activeId = rosters[0].id; loaded = true;
  });

  const fmt = (value: number) => new Intl.NumberFormat('pt-BR').format(value);
  function fmtK(value: number): string {
    if (value % 1000 === 0 && value >= 1000) return (value / 1000) + 'K';
    return fmt(value);
  }
  function raidModeClass(mode: string) { return `mode-${mode.toLowerCase()}`; }
  function raidById(id: string) { return raids.find((r) => r.id === id); }
  function suggestedRaidsForLevel(level: number) {
    const bestPerBoss = raidBosses.map((boss) => raids
      .filter((raid) => raid.boss === boss && raid.level <= level)
      .sort((a, b) => b.level - a.level || modeRank[b.mode] - modeRank[a.mode] || b.gold - a.gold)[0]
    ).filter((raid): raid is Raid => Boolean(raid));

    return bestPerBoss
      .sort((a, b) => b.level - a.level || modeRank[b.mode] - modeRank[a.mode] || b.gold - a.gold)
      .slice(0, 3)
      .map((raid) => raid.id);
  }
  function createCharacter(nick: string, level: number, className: string): Character {
    return { id: crypto.randomUUID(), nick, level, className, raids: suggestedRaidsForLevel(level) };
  }
  function splitGold(raid: Raid, characterLevel: number) {
    if (raid.padre) return { character: raid.gold, free: 0, roster: 0 };
    if (characterLevel <= 1710) return { character: 0, free: raid.gold / 2, roster: raid.gold / 2 };
    if (raid.normal) return { character: 0, free: raid.gold / 2, roster: raid.gold / 2 };
    return { character: 0, free: raid.gold, roster: 0 };
  }
  function characterTotals(character: Character) {
    return character.raids.reduce((sum, id) => {
      const raid = raidById(id); if (!raid) return sum;
      const part = splitGold(raid, character.level);
      return { character: sum.character + part.character, free: sum.free + part.free, roster: sum.roster + part.roster };
    }, { character: 0, free: 0, roster: 0 });
  }
  let totals = $derived(earners.reduce((sum, char) => {
    const part = characterTotals(char);
    return { character: sum.character + part.character, free: sum.free + part.free, roster: sum.roster + part.roster };
  }, { character: 0, free: 0, roster: 0 }));

  async function persist(next: Roster) {
    rosters = rosters.map((r) => r.id === next.id ? next : r); await saveRoster(next);
  }
  async function createRoster() {
    const name = newRosterName.trim(); if (!name) return;
    const roster: Roster = { id: crypto.randomUUID(), name, createdAt: Date.now(), characters: [] };
    rosters = [...rosters, roster]; activeId = roster.id; newRosterName = ''; showRosterForm = false; await saveRoster(roster);
  }
  async function removeRoster() {
    if (!active || rosters.length === 1 || !confirm(`Excluir o roster "${active.name}"?`)) return;
    await deleteRoster(active.id); rosters = rosters.filter((r) => r.id !== active.id); activeId = rosters[0].id; menuOpen = false;
  }
  async function renameRoster() {
    const name = renameRosterName.trim();
    if (!active || !name) return;
    await persist({ ...active, name });
    renameRosterName = ''; showRenameRoster = false; menuOpen = false;
  }
  async function addCharacter() {
    if (!active || !draft.nick.trim() || !draft.level || draft.level < 1 || !draft.className) return;
    const level = Number(draft.level);
    const character = createCharacter(draft.nick.trim(), level, draft.className);
    await persist({ ...active, characters: [...active.characters, character] });
    draft = { nick: '', level: undefined, className: '' }; showCharacterForm = false;
  }
  async function importRosterFromApi() {
    const characterName = importDraft.characterName.trim();
    if (!active || !characterName || importLoading) return;

    importLoading = true;
    importError = '';
    importMessage = '';

    try {
      const apiCharacters = await BibleApiService.fetchFullRoster(importDraft.region, characterName);
      const seenNames = new Set(active.characters.map((character) => character.nick.toLowerCase()));
      const importedCharacters: Character[] = [];

      for (const apiCharacter of apiCharacters) {
        const normalized = normalizeApiCharacter(apiCharacter);
        if (!normalized || seenNames.has(normalized.nick.toLowerCase())) continue;

        importedCharacters.push(createCharacter(normalized.nick, normalized.level, normalized.className));
        seenNames.add(normalized.nick.toLowerCase());
      }

      if (!importedCharacters.length) {
        importMessage = 'Nenhum personagem novo encontrado para importar.';
        return;
      }

      await persist({ ...active, characters: [...active.characters, ...importedCharacters] });
      importDraft.characterName = '';
      importMessage = `${importedCharacters.length} personagem${importedCharacters.length === 1 ? '' : 's'} importado${importedCharacters.length === 1 ? '' : 's'} com sucesso.`;
    } catch (error) {
      importError = error instanceof Error ? error.message : 'Falha ao importar personagens.';
    } finally {
      importLoading = false;
    }
  }
  function normalizeApiCharacter(character: BibleRosterCharacter) {
    const nick = character.name.trim();
    const className = character.class.trim();
    const level = Number(character.ilvl);

    if (!nick || !className || !Number.isFinite(level) || level <= 0) return null;
    return { nick, className, level };
  }
  async function removeCharacter(id: string) {
    if (!active) return; await persist({ ...active, characters: active.characters.filter((c) => c.id !== id) });
    confirmCharacterId = null;
  }
  async function toggleRaid(character: Character, raid: Raid) {
    if (!active || character.level < raid.level) return;
    const selected = character.raids.includes(raid.id);
    const selectedSameBoss = character.raids.find((id) => raidById(id)?.boss === raid.boss);
    if (!selected && !selectedSameBoss && character.raids.length >= 3) return;
    const raidsWithoutSameBoss = character.raids.filter((id) => raidById(id)?.boss !== raid.boss);
    const nextChar = { ...character, raids: selected ? raidsWithoutSameBoss : [...raidsWithoutSameBoss, raid.id] };
    await persist({ ...active, characters: active.characters.map((c) => c.id === character.id ? nextChar : c) });
  }
</script>

<svelte:head><title>Ark Ledger — Calculadora de Gold</title><meta name="description" content="Organize seu roster e calcule o gold semanal de Lost Ark." /></svelte:head>

{#if loaded}
  <header>
    <button class="roster-trigger" onclick={() => rosterDrawerOpen = true}>{active?.name ?? 'Roster'} <span>{earners.length}/6</span></button>
    <section class="summary header-summary">
      <div><span class="summary-icon character">◇</span><p>CHARACTER <small>Bound to character</small></p><strong>{fmt(totals.character)}</strong></div>
      <div><span class="summary-icon roster">⬡</span><p>ROSTER <small>Bound to roster</small></p><strong>{fmt(totals.roster)}</strong></div>
      <div><span class="summary-icon free">✦</span><p>TRADABLE <small>Disponível para uso</small></p><strong>{fmt(totals.free)}</strong></div>
      <div><span class="summary-icon gold">◆</span><p>GOLD TOTAL <small>Todas as recompensas</small></p><strong>{fmt(totals.character + totals.free + totals.roster)}</strong></div>
    </section>
  </header>

  {#if rosterDrawerOpen}
    <button class="drawer-backdrop" aria-label="Fechar drawer do roster" onclick={() => rosterDrawerOpen = false}></button>
    <aside class="roster-drawer" aria-label="Gerenciar roster">
      <div class="drawer-head"><div><p class="eyebrow">GERENCIAR</p><h2>Roster</h2></div><button class="drawer-close" aria-label="Fechar" onclick={() => rosterDrawerOpen = false}>×</button></div>
      {#if !showCharacterForm}
        <section class="roster-bar">
          <div class="roster-tabs">
            {#each rosters as roster}
              <button class:active={roster.id === activeId} onclick={() => activeId = roster.id}>{roster.name}<small>{roster.characters.length} personagens</small></button>
            {/each}
            <button class="new-roster" onclick={() => showRosterForm = true}>＋ Novo roster</button>
          </div>
          <div class="roster-tools"><button class="rename-trigger" onclick={() => { renameRosterName = active?.name ?? ''; showRenameRoster = true; menuOpen = false; }}>Renomear</button><div class="menu-wrap"><button class="icon-button" aria-label="Menu do roster" onclick={() => menuOpen = !menuOpen}>•••</button>{#if menuOpen}<div class="roster-menu"><button class="danger" onclick={removeRoster} disabled={rosters.length === 1}>Excluir roster</button></div>{/if}</div></div>
        </section>
        {#if showRenameRoster}
          <form class="inline-form rename-form" onsubmit={(e) => { e.preventDefault(); renameRoster(); }}><input bind:value={renameRosterName} placeholder="Novo nome do roster" maxlength="32"><button class="primary">Salvar nome</button><button type="button" class="ghost" onclick={() => showRenameRoster = false}>Cancelar</button></form>
        {/if}
        {#if showRosterForm}
          <form class="inline-form" onsubmit={(e) => { e.preventDefault(); createRoster(); }}><input bind:value={newRosterName} placeholder="Nome do novo roster" maxlength="32"><button class="primary">Criar</button><button type="button" class="ghost" onclick={() => showRosterForm = false}>Cancelar</button></form>
        {/if}
        <form class="import-form" onsubmit={(e) => { e.preventDefault(); importRosterFromApi(); }}>
          <div>
            <p class="eyebrow">IMPORTAR DA API</p>
            <strong>Buscar roster por personagem</strong>
          </div>
          <label>Região<select bind:value={importDraft.region} disabled={importLoading}><option value="NA">NA</option><option value="EU">EU</option></select></label>
          <label>Personagem<input bind:value={importDraft.characterName} placeholder="Nome do personagem" disabled={importLoading}></label>
          <button class="primary" disabled={importLoading}>{importLoading ? 'Importando...' : 'Importar'}</button>
          {#if importMessage}<p class="import-status">{importMessage}</p>{/if}
          {#if importError}<p class="import-status error">{importError}</p>{/if}
        </form>
      {/if}
      <div class="drawer-action"><div><p class="eyebrow">PERSONAGENS</p><strong>{earners.length} de 6 gold earners</strong></div><button class="primary" onclick={() => showCharacterForm = true}>＋ Adicionar</button></div>
      {#if showCharacterForm}
        <form class="character-form" onsubmit={(e) => { e.preventDefault(); addCharacter(); }}>
          <label>Nick<input required bind:value={draft.nick} placeholder="Nome do personagem"></label>
          <label>Item level<input required type="number" min="1" bind:value={draft.level} placeholder="Ex.: 1750"></label>
          <label>Classe<select required bind:value={draft.className}><option value="" disabled>Selecione uma classe</option>{#each classes as cls}<option>{cls}</option>{/each}</select></label>
          <div class="form-actions">
            <button class="primary">Adicionar</button>
            <button type="button" class="ghost" onclick={() => showCharacterForm = false}>Cancelar</button>
          </div>
        </form>

        {#if active?.characters.length}
          <div class="drawer-character-list">
            <p class="eyebrow">Personagens no Roster</p>
            {#each active.characters as character}
              <div class="drawer-character-item">
                <div class="drawer-character-info">
                  <span class="nick">{character.nick}</span>
                  <span class="info">{character.className} · {character.level}</span>
                </div>
                {#if confirmCharacterId === character.id}
                  <div class="confirm-remove">
                    <span>Remover?</span>
                    <button class="confirm-yes" onclick={() => removeCharacter(character.id)}>Sim</button>
                    <button class="confirm-no" onclick={() => confirmCharacterId = null}>Não</button>
                  </div>
                {:else}
                  <button class="remove-char-btn" aria-label="Remover personagem" onclick={() => confirmCharacterId = character.id}>×</button>
                {/if}
              </div>
            {/each}
          </div>
        {/if}
      {/if}
    </aside>
  {/if}

  <main id="calculator">
    {#if earners.length}
      <div class="characters-board">
        {#each earners as character, index (character.id)}
          {@const ct = characterTotals(character)}
          <article class="character-card">
            <div class="character-head"><div><h3>{character.nick}</h3><p>{character.className} · <b>{character.level}</b></p></div><span class="earner-badge">{index + 1}/6</span></div>
            <div class="raid-list">
              {#each raidBosses as boss}
                <div class="raid-separator"><span>{boss}</span></div>
                <div class="boss-modes">
                  {#each raids.filter((raid) => raid.boss === boss).sort((a, b) => b.level - a.level || modeRank[b.mode] - modeRank[a.mode]) as raid}
                    {@const locked = character.level < raid.level}
                    <button class={raidModeClass(raid.mode)} class:selected={character.raids.includes(raid.id)} class:locked onclick={() => toggleRaid(character, raid)} disabled={locked} title={locked ? `Requer item level ${raid.level}` : ''}>
                      <span class="check">{character.raids.includes(raid.id) ? '✓' : locked ? '⌁' : ''}</span>
                      <span class="info-col"><b>{raid.mode}</b></span>
                      <strong>{fmtK(raid.gold)}</strong>
                    </button>
                  {/each}
                </div>
              {/each}
            </div>
            <footer><span>Gold deste personagem</span><b>{fmtK(ct.character + ct.free + ct.roster)} <small>gold</small></b></footer>
          </article>
        {/each}
      </div>
    {:else}
      <div class="empty"><div>♙</div><h3>Seu roster está vazio</h3><p>Adicione seu primeiro personagem para começar a planejar a semana.</p><button class="primary" onclick={() => { rosterDrawerOpen = true; showCharacterForm = true; }}>＋ Adicionar personagem</button></div>
    {/if}

    {#if reserves.length}
      <section class="reserves"><p class="eyebrow">RESERVAS · NÃO ENTRAM NO CÁLCULO</p><div>{#each reserves as character}<article><span><b>{character.nick}</b><small>{character.className} · {character.level}</small></span><mark>SEM GOLD</mark></article>{/each}</div></section>
    {/if}

  </main>
{/if}
