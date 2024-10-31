import {
    Flask,
    User,
    Database,
    Function,
    ListMagnifyingGlass,
    ChartLineUp,
    TreeStructure,
    BracketsAngle,
    BookOpenText,
    GithubLogo,
    Pinwheel
} from 'phosphor-svelte';

export const routes = [
    { name: '', title: true },
    { name: 'Inspect', path: '/inspect', icon: ListMagnifyingGlass },
    { name: 'Playground', path: '/playground', icon: Pinwheel },
    { name: 'State Machines', path: '/state-machines', icon: TreeStructure, disabled: true },
    { name: 'Performance', path: '/performance', icon: ChartLineUp, disabled: true },
    { name: 'Analyze', path: '/analyze', icon: Function, disabled: true },
    { name: 'Datasets', path: '/datasets', icon: Database, disabled: true },
    { name: 'Experiments', path: '/experiments', icon: Flask, disabled: true },
    { name: 'Community', title: true },
    { name: 'Patterns Hub', path: '/patterns-hub', icon: BracketsAngle, disabled: true },
    { name: 'Learn', title: true },
    { name: 'Documentation', path: 'http://localhost:8002/documentation', icon: BookOpenText },
    { name: 'Github', path: 'https://github.com/flou-ai/flou-private/', icon: GithubLogo },
    { name: 'Bottom', section: true },
    { name: 'My profile', path: '/profile', icon: User, disabled: true, showInNav: false },
];
