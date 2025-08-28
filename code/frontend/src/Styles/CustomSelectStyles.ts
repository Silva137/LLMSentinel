import {GroupBase, StylesConfig} from "react-select";

export interface SelectOptionType {
    value: string;
    label: string;
}

export const customSelectStyles: StylesConfig<SelectOptionType, false, GroupBase<SelectOptionType>> = {
    control: (provided, state) => ({
        ...provided,
        backgroundColor: '#1e2235',
        borderColor: state.isFocused ? '#6a6fbf' : '#363c58',
        boxShadow: state.isFocused ? '0 0 0 1px #6a6fbf' : 'none',
        borderRadius: '8px',
        minHeight: '40px',
        color: '#e0e4ff',
        fontSize: '0.9rem',
        minWidth: '200px',
        width: '200px',
        '&:hover': { borderColor: '#6a6fbf' },
    }),
    menu: (provided) => ({
        ...provided,
        backgroundColor: '#2f354c',
        borderRadius: '8px',
        marginTop: '4px',
        zIndex: 10,
    }),
    option: (provided, state) => ({
        ...provided,
        backgroundColor: state.isSelected ? '#6a6fbf' : state.isFocused ? '#3b4262' : '#2f354c',
        color: state.isSelected ? 'white' : '#e0e4ff',
        padding: '10px 12px',
        cursor: 'pointer',
        fontSize: '0.9rem',
        '&:active': { backgroundColor: '#5564ae' },
    }),
    singleValue: (provided) => ({ ...provided, color: '#e0e4ff' }),
    placeholder: (provided) => ({ ...provided, color: '#a0a7d3' }),
    input: (provided) => ({ ...provided, color: '#e0e4ff' }),
    dropdownIndicator: (provided) => ({ ...provided, color: '#a0a7d3', '&:hover': { color: '#e0e4ff' }}),
    clearIndicator: (provided) => ({ ...provided, color: '#a0a7d3', '&:hover': { color: '#e0e4ff' }}),
    menuList: (provided) => ({
        ...provided,
        '&::-webkit-scrollbar': { width: '8px' },
        '&::-webkit-scrollbar-track': { background: '#2a2f45', borderRadius: '10px' },
        '&::-webkit-scrollbar-thumb': { backgroundColor: '#4a5175', borderRadius: '10px', border: '2px solid #2a2f45' },
        '&::-webkit-scrollbar-thumb:hover': { backgroundColor: '#5a67d8' },
        scrollbarWidth: 'thin',
        scrollbarColor: '#4a5175 #2a2f45',
    }),
};

export const customSelectStylesModal: StylesConfig<SelectOptionType, false, GroupBase<SelectOptionType>> = {
    ...customSelectStyles,
    control: (provided, state) => {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-expect-error
        const base = (customSelectStyles.control)(provided, state);
        return {
            ...base,
            minWidth: 200,
            width: '95%',
        };
    },
};