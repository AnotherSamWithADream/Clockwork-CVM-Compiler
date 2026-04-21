const fs = require('fs');

const MAX_STEPS = 360 * 1000000;
const opsList = ["give", "take", "drop", "gen", "copy", "send", "ifzflip", "ifzhalt"];

class ClockworkSimulator {
    constructor(bitwidth, operations, rings, inputs) {
        this.bitwidth = bitwidth;
        this.operations = operations;
        this.rings = rings;
        this.inputsCount = inputs;

        const numLayers = rings.length - 1;
        this.layerAlignments = Array.from({ length: numLayers }, () => ({}));
        const offsetsSet = new Set();

        for (let k = 0; k < numLayers; k++) {
            const kRotating = (k % 2 === 1);
            for (let i2 = 0; i2 < rings[k].length; i2++) {
                const inner = rings[k][i2];
                for (let j2 = 0; j2 < rings[k + 1].length; j2++) {
                    const outer = rings[k + 1][j2];
                    let offset, angle;
                    if (kRotating) {
                        offset = (outer.original - inner.original) % 360;
                        if (offset < 0) offset += 360;
                        angle = outer.original;
                    } else {
                        offset = (inner.original - outer.original) % 360;
                        if (offset < 0) offset += 360;
                        angle = inner.original;
                    }
                    if (!this.layerAlignments[k][offset]) {
                        this.layerAlignments[k][offset] = [];
                    }
                    this.layerAlignments[k][offset].push([angle, k, i2, k + 1, j2]);
                    offsetsSet.add(offset);
                }
            }
            
            for (const offset in this.layerAlignments[k]) {
                this.layerAlignments[k][offset].sort((a, b) => a[0] - b[0]);
            }
        }

        this.offsetsSorted = Array.from(offsetsSet).sort((a, b) => a - b);
        this.numOffsets = this.offsetsSorted.length;

        if (this.numOffsets > 0) {
            this.offsetActions = [];
            for (let i = 0; i < this.numOffsets; i++) {
                const offset = this.offsetsSorted[i];
                const actions = [];
                for (let bitIdx = 0; bitIdx < this.bitwidth; bitIdx++) {
                    const bit = 1 << bitIdx;
                    for (let k = 0; k < numLayers; k++) {
                        const entries = this.layerAlignments[k][offset];
                        if (!entries) continue;
                        for (const entry of entries) {
                            const [angle, i1, i2, j1, j2] = entry;
                            const m1 = this.rings[i1][i2];
                            const m2 = this.rings[j1][j2];
                            if ((m1.bitstring & m2.bitstring & bit) !== 0) {
                                actions.push([this.operations[bitIdx], i1, i2, j1, j2]);
                            }
                        }
                    }
                }
                this.offsetActions.push(actions);
            }

            this.deltaCw = [];
            this.deltaCcw = [];
            for (let i = 0; i < this.numOffsets; i++) {
                const nextCw = (i + 1) % this.numOffsets;
                const nextCcw = (i - 1 + this.numOffsets) % this.numOffsets;
                
                let dcw = (this.offsetsSorted[nextCw] - this.offsetsSorted[i]) % 360;
                if (dcw <= 0) dcw += 360;
                
                let dccw = (this.offsetsSorted[i] - this.offsetsSorted[nextCcw]) % 360;
                if (dccw <= 0) dccw += 360;

                this.deltaCw.push(dcw);
                this.deltaCcw.push(dccw);
            }
        } else {
            this.offsetActions = [];
            this.deltaCw = [];
            this.deltaCcw = [];
        }

        this.reset();
    }

    reset() {
        for (const ring of this.rings) {
            for (const m of ring) {
                m.pos = m.original;
                m.value = m.initial_value !== undefined ? m.initial_value : 0;
            }
        }
        this.dir = 1;
        this.stepCount = 0;
        this.offset = 0;
        this.offsetIdx = -1;
    }

    inject(inp) {
        if (inp.length !== this.inputsCount) {
            throw new Error(`Wrong input count: ${inp.length}`);
        }
        for (const ring of this.rings) {
            for (const m of ring) {
                if (m.input_pos !== -1) {
                    m.value = inp[m.input_pos];
                }
            }
        }
    }

    binarySearchRight(arr, val) {
        let left = 0, right = arr.length;
        while (left < right) {
            const mid = Math.floor((left + right) / 2);
            if (arr[mid] <= val) left = mid + 1;
            else right = mid;
        }
        return left;
    }

    binarySearchLeft(arr, val) {
        let left = 0, right = arr.length;
        while (left < right) {
            const mid = Math.floor((left + right) / 2);
            if (arr[mid] < val) left = mid + 1;
            else right = mid;
        }
        return left;
    }

    step() {
        if (this.stepCount >= MAX_STEPS || this.numOffsets === 0) {
            this.stepCount = MAX_STEPS;
            return null;
        }

        let delta;
        if (this.offsetIdx === -1) {
            if (this.dir === 1) {
                const idx = this.binarySearchRight(this.offsetsSorted, this.offset) % this.numOffsets;
                delta = (this.offsetsSorted[idx] - this.offset) % 360;
                if (delta <= 0) delta += 360;
                this.offsetIdx = idx;
            } else {
                let idx = this.binarySearchLeft(this.offsetsSorted, this.offset) - 1;
                if (idx < 0) idx += this.numOffsets;
                delta = (this.offset - this.offsetsSorted[idx]) % 360;
                if (delta <= 0) delta += 360;
                this.offsetIdx = idx;
            }
            this.offset = this.offsetsSorted[this.offsetIdx];
        } else {
            if (this.dir === 1) {
                const idx = (this.offsetIdx + 1) % this.numOffsets;
                delta = this.deltaCw[this.offsetIdx];
                this.offsetIdx = idx;
            } else {
                const idx = (this.offsetIdx - 1 + this.numOffsets) % this.numOffsets;
                delta = this.deltaCcw[this.offsetIdx];
                this.offsetIdx = idx;
            }
            this.offset = this.offsetsSorted[this.offsetIdx];
        }

        if (this.stepCount + delta > MAX_STEPS) {
            this.stepCount = MAX_STEPS;
            return null;
        }
        this.stepCount += delta;

        const actions = this.offsetActions[this.offsetIdx];
        for (let i = 0; i < actions.length; i++) {
            const [op, i1, i2, j1, j2] = actions[i];
            const mInner = this.rings[i1][i2];
            const mOuter = this.rings[j1][j2];

            if (op === "give") {
                if (mOuter.value !== 0) { mOuter.value--; mInner.value++; }
            } else if (op === "take") {
                if (mInner.value !== 0) { mOuter.value++; mInner.value--; }
            } else if (op === "drop") {
                if (mInner.value !== 0 && mOuter.value !== 0) { mInner.value--; mOuter.value--; }
            } else if (op === "gen") {
                mInner.value++; mOuter.value++;
            } else if (op === "copy") {
                mOuter.value += mInner.value;
            } else if (op === "send") {
                mInner.value += mOuter.value; mOuter.value = 0;
            } else if (op === "ifzflip") {
                if (mInner.value === 0) { this.dir *= -1; }
            } else if (op === "ifzhalt") {
                if (mInner.value === 0) { return this.rings[0][0].value; }
            }
        }
        return undefined;
    }

    simulate(inp) {
        this.reset();
        this.inject(inp);
        while (this.stepCount < MAX_STEPS) {
            const result = this.step();
            if (result !== undefined && result !== null) {
                return result;
            }
            if (result === null) return null;
        }
        return null;
    }
}

class ClockworkEngine {
    static parseCode(codePath) {
        const code = JSON.parse(fs.readFileSync(codePath, 'utf8'));
        const bitwidth = code.bitwidth;
        const operations = code.operations;
        const rings = code.rings;

        let inputs = [];
        let markers = 0;
        let realRings = [];

        for (const ring of rings) {
            let nextRing = [];
            markers += ring.length;
            const positions = new Set();
            for (const m of ring) {
                positions.add(m.position);
                const bitstring = parseInt(m.bitstring.split('').reverse().join(''), 2);
                const marker = {
                    original: m.position,
                    pos: m.position,
                    bitstring: bitstring,
                    input_pos: m.input !== undefined ? m.input : -1,
                    initial_value: m.value !== undefined ? m.value : 0,
                    value: m.value !== undefined ? m.value : 0
                };
                if (m.input !== undefined) {
                    inputs.push(m.input);
                }
                nextRing.push(marker);
            }
            realRings.push(nextRing);
        }
        
        inputs.sort((a, b) => a - b);
        
        return {
            simulator: new ClockworkSimulator(bitwidth, operations, realRings, inputs.length),
            numRings: realRings.length,
            numMarkers: markers
        };
    }

    static parseTests(testPath) {
        return JSON.parse(fs.readFileSync(testPath, 'utf8'));
    }

    grade(codePath, testPath, verbose = false) {
        const { simulator, numRings, numMarkers } = ClockworkEngine.parseCode(codePath);
        const tests = ClockworkEngine.parseTests(testPath);

        let numPassTests = 0;
        for (const testCase of tests) {
            if (verbose) console.log(`Running test with input [${testCase.input}]`);
            const output = simulator.simulate(testCase.input);

            if (output === null) {
                if (verbose) console.log("Maximum steps exceeded");
            } else {
                if (output === testCase.output[0]) {
                    numPassTests++;
                    if (verbose) console.log("Success");
                } else {
                    if (verbose) console.log(`Fail, gave ${output} when expected is ${testCase.output[0]}`);
                }
            }
        }

        return {
            testPath,
            numTests: tests.length,
            numPassTests,
            numBits: simulator.bitwidth,
            numMarkers,
            numRings
        };
    }
}

if (require.main === module) {
    const args = process.argv.slice(2);
    let codePath, testPath, verbose = false;
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '-c' || args[i] === '--code') codePath = args[++i];
        if (args[i] === '-t' || args[i] === '--tests') testPath = args[++i];
        if (args[i] === '-v' || args[i] === '--verbose') verbose = true;
    }

    if (!codePath || !testPath) {
        console.error("Usage: node engine.js -c code.json -t tests.json [-v]");
        process.exit(1);
    }

    const engine = new ClockworkEngine();
    const result = engine.grade(codePath, testPath, verbose);
    console.log(`Passed ${result.numPassTests} out of ${result.numTests} cases.`);
    process.exit(result.numPassTests === result.numTests ? 0 : 1);
}
