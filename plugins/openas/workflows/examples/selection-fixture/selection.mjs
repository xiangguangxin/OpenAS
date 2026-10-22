// Deliberately broken state update for the isolated frontend repair example.
export function toggleSelection(selectedIds, id) {
  selectedIds.push(id);
  return selectedIds;
}
