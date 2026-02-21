/**
 * Options Widget — rendered inside a chat message to present user with
 * a set of choices for how they want to proceed with their analysis.
 */

import React from 'react';
import { OptionsWidgetChoice } from '../api/types';
import styles from './OptionsWidget.module.css';

interface OptionsWidgetProps {
  choices: OptionsWidgetChoice[];
  onChoice: (choiceId: string) => void;
  disabled?: boolean;
}

export const OptionsWidget: React.FC<OptionsWidgetProps> = ({ choices, onChoice, disabled }) => {
  return (
    <div className={styles.widget}>
      {choices.map(choice => (
        <button
          key={choice.id}
          className={`${styles.choice} ${disabled ? styles.disabled : ''}`}
          onClick={() => !disabled && onChoice(choice.id)}
          disabled={disabled}
        >
          {choice.label}
        </button>
      ))}
    </div>
  );
};
