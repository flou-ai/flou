export let getDottedPath = (state: any, fqn: string, rootInstance: string | null = null) => {
    const keys = fqn.split('.');
    if (rootInstance) {
        const rootKeys = rootInstance.split('.');

        // merge both arrays keeping rootKeys then the keys
        for (let i = 0; i < rootKeys.length; i++) {
            keys[i] = rootKeys[i];
        }
    }

    keys.shift(); // discard root fqn
    let currentValue = state;

    for (const key of keys) {
        if (currentValue[key] === undefined) {
            return undefined; // Return undefined if the key does not exist
        }
        currentValue = currentValue[key];
    }
    return currentValue;
}

export let getFQNStructure = (structure: any, keys: string[]) => {
    keys.shift(); // discard root fqn
    let currentValue = structure;

    for (const key of keys) {
        if (currentValue.ltms === undefined) {
            return undefined; // Return undefined if there are no ltms
        }
        for (const ltm of currentValue.ltms) {
            if (ltm.name === key) {
                currentValue = ltm;
                break;
            }
        }
    }
    return currentValue;
}

export let getNodeStatus = (state: any, structure: any, fqn: string, currentRootInstance: string) => {
    let nodeState = getDottedPath(state, fqn, currentRootInstance);

    let parentFQNKeys = fqn.split('.');
    parentFQNKeys.pop(); // remove last key to get parent
    let parentTransitions = getFQNStructure(structure, parentFQNKeys).transitions;
    if (nodeState) {
        if (nodeState._status === 'active') {
            // node is active
            let nodeStructure = getFQNStructure(structure, fqn.split('.'));
            if (nodeStructure.ltms) { // is parent
                // check if every child is 'finished'
                if (nodeStructure.ltms.every((ltm: any) => getNodeStatus(state, structure, ltm.fqn, currentRootInstance) === 'finished')) {
                    return 'finished';
                }
            }
        }
        return nodeState._status;
    }
}

export let ltmToGraph = (_ltm: any | null = null, parentFQN: string | null = null): any => {
    if (!parentFQN) {
        parentFQN = _ltm.fqn;
    }

    let elements = [];

    if (!_ltm.ltms) {
        return [];
    }
    for (let sub of _ltm.ltms) {
        let element: any = {
            data: {
                id: sub.fqn,
                label: sub.name
            }
        };
        if (parentFQN) {
            element.data.parent = parentFQN;
        }
        if (_ltm.init.includes(sub.name)) {
            element.classes = 'start';
            element.data.init = true;
        }
        if (sub.ltms) {
            element.data.isParent = true;
        }
        elements.push(element);

        elements.push(...ltmToGraph(sub, sub.fqn));
    }

    // Add the transitions
    if (_ltm.transitions) {
        for (let edge of _ltm.transitions) {
            let data: any = {
                source: `${_ltm.fqn}.${edge.from}`,
                target: `${_ltm.fqn}.${edge.to}`,
                label: edge.label,
                namespace: edge.namespace,
                displayLabel: edge.display_label,
            }
            elements.push({ data });
        }
    }

    return elements;
};

/// fqn matching

interface MatchResult {
    placeholder: string;
    value: string;
}

export function matchFQN(pattern: string, target: string): { isMatch: boolean, matches: MatchResult[] } {
    // Create an array to hold the placeholder names
    const placeholders: string[] = [];

    // Build a regex pattern that captures both the placeholder names and their values
    const regexPattern = pattern.replace(/{([^}]+)}/g, (fullMatch, placeholderName) => {
        placeholders.push(placeholderName);
        return '([^\\.]+)'; // Create a capture group for each placeholder
    });

    // Create a regular expression from the modified pattern
    const regex = new RegExp(`^${regexPattern}$`);

    // Test the target string and extract matches
    const match = target.match(regex);

    if (!match) {
        return { isMatch: false, matches: [] }; // Return no matches if the pattern does not match
    }

    // Extract the matched values and map them to their corresponding placeholder names
    const matches: MatchResult[] = placeholders.map((placeholder, index) => ({
        placeholder,
        value: match[index + 1], // match[0] is the full match, so we start from index 1
    }));

    return { isMatch: true, matches };
}

export let fqnToJsonPatchPath = (fqn: string): string  => {

    let keys = fqn.split('.');
    keys.shift(); // remove root key

    const innerPath = keys.join('/');
    return `/${innerPath}/`;
}