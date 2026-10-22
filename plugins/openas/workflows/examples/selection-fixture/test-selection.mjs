import assert from 'node:assert/strict';
import {toggleSelection} from './selection.mjs';

assert.deepEqual(toggleSelection([], 'a'), ['a']);
assert.deepEqual(toggleSelection(['a', 'b'], 'a'), ['b']);
assert.deepEqual(toggleSelection(['a'], 'b'), ['a', 'b']);
const original = ['a'];
const next = toggleSelection(original, 'b');
assert.deepEqual(original, ['a']);
assert.notEqual(next, original);
assert.deepEqual(toggleSelection(next, 'b'), original);
console.log('Selection state checks passed; no browser or real UI was exercised.');
