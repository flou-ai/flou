export const formatDate = (dateString: string) => {
    const options = {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    } as const;
    return new Date(dateString).toLocaleDateString(undefined, options);
};
