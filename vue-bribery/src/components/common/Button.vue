<template>
  <component 
    :is="tag" 
    class="custom-button" 
    :class="[
      `variant-${variant}`,
      { 
        'size-small': size === 'small',
        'size-large': size === 'large',
        'is-loading': loading,
        'is-block': block,
        'is-rounded': rounded,
        'is-outlined': outlined,
        'is-text': text,
        'is-icon-only': iconOnly
      }
    ]" 
    :disabled="disabled || loading"
    v-bind="$attrs"
  >
    <span class="button-content" :class="{ 'invisible': loading }">
      <component 
        v-if="icon && iconPosition === 'left'" 
        :is="icon" 
        class="button-icon button-icon-left" 
      />
      <span v-if="!iconOnly" class="button-label">
        <slot>Button</slot>
      </span>
      <component 
        v-if="icon && iconPosition === 'right'" 
        :is="icon" 
        class="button-icon button-icon-right" 
      />
    </span>

    <span v-if="loading" class="button-loader">
      <span class="loader-dot"></span>
      <span class="loader-dot"></span>
      <span class="loader-dot"></span>
    </span>
  </component>
</template>

<script>
export default {
  name: 'Button',
  
  inheritAttrs: false,

  props: {
    variant: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'neutral'].includes(value)
    },
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    loading: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    block: {
      type: Boolean,
      default: false
    },
    rounded: {
      type: Boolean,
      default: false
    },
    outlined: {
      type: Boolean,
      default: false
    },
    text: {
      type: Boolean,
      default: false
    },
    icon: {
      type: [Object, Function],
      default: null
    },
    iconPosition: {
      type: String,
      default: 'left',
      validator: (value) => ['left', 'right'].includes(value)
    },
    iconOnly: {
      type: Boolean,
      default: false
    },
    tag: {
      type: String,
      default: 'button'
    }
  }
}
</script>

<style scoped>
.custom-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.5;
  border-radius: 0.25rem;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease-in-out;
  text-decoration: none;
  border: 1px solid transparent;
  outline: none;
}

/* Size variants */
.size-small {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
}

.size-large {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}

/* Display variants */
.is-block {
  display: flex;
  width: 100%;
}

.is-rounded {
  border-radius: 999px;
}

/* Color variants */
.variant-primary {
  background-color: var(--primary-color, #0080ff);
  color: white;
}
.variant-primary:hover:not(:disabled) {
  background-color: color-mix(in srgb, var(--primary-color, #0080ff) 90%, black);
}

.variant-secondary {
  background-color: var(--secondary-color, #ff4081);
  color: white;
}
.variant-secondary:hover:not(:disabled) {
  background-color: color-mix(in srgb, var(--secondary-color, #ff4081) 90%, black);
}

.variant-success {
  background-color: var(--success-color, #4caf50);
  color: white;
}
.variant-success:hover:not(:disabled) {
  background-color: color-mix(in srgb, var(--success-color, #4caf50) 90%, black);
}

.variant-danger {
  background-color: var(--error-color, #f44336);
  color: white;
}
.variant-danger:hover:not(:disabled) {
  background-color: color-mix(in srgb, var(--error-color, #f44336) 90%, black);
}

.variant-warning {
  background-color: var(--warning-color, #ff9800);
  color: white;
}
.variant-warning:hover:not(:disabled) {
  background-color: color-mix(in srgb, var(--warning-color, #ff9800) 90%, black);
}

.variant-info {
  background-color: var(--info-color, #2196f3);
  color: white;
}
.variant-info:hover:not(:disabled) {
  background-color: color-mix(in srgb, var(--info-color, #2196f3) 90%, black);
}

.variant-neutral {
  background-color: #e0e0e0;
  color: #333;
}
.variant-neutral:hover:not(:disabled) {
  background-color: #d0d0d0;
}

/* Outlined variants */
.is-outlined {
  background-color: transparent;
  border-width: 1px;
}

.variant-primary.is-outlined {
  border-color: var(--primary-color, #0080ff);
  color: var(--primary-color, #0080ff);
}
.variant-primary.is-outlined:hover:not(:disabled) {
  background-color: rgba(0, 128, 255, 0.1);
}

.variant-secondary.is-outlined {
  border-color: var(--secondary-color, #ff4081);
  color: var(--secondary-color, #ff4081);
}
.variant-secondary.is-outlined:hover:not(:disabled) {
  background-color: rgba(255, 64, 129, 0.1);
}

.variant-success.is-outlined {
  border-color: var(--success-color, #4caf50);
  color: var(--success-color, #4caf50);
}
.variant-success.is-outlined:hover:not(:disabled) {
  background-color: rgba(76, 175, 80, 0.1);
}

.variant-danger.is-outlined {
  border-color: var(--error-color, #f44336);
  color: var(--error-color, #f44336);
}
.variant-danger.is-outlined:hover:not(:disabled) {
  background-color: rgba(244, 67, 54, 0.1);
}

.variant-warning.is-outlined {
  border-color: var(--warning-color, #ff9800);
  color: var(--warning-color, #ff9800);
}
.variant-warning.is-outlined:hover:not(:disabled) {
  background-color: rgba(255, 152, 0, 0.1);
}

.variant-info.is-outlined {
  border-color: var(--info-color, #2196f3);
  color: var(--info-color, #2196f3);
}
.variant-info.is-outlined:hover:not(:disabled) {
  background-color: rgba(33, 150, 243, 0.1);
}

.variant-neutral.is-outlined {
  border-color: #bdbdbd;
  color: #757575;
}
.variant-neutral.is-outlined:hover:not(:disabled) {
  background-color: rgba(0, 0, 0, 0.05);
}

/* Text variants */
.is-text {
  background-color: transparent;
  border-color: transparent;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.variant-primary.is-text {
  color: var(--primary-color, #0080ff);
}
.variant-primary.is-text:hover:not(:disabled) {
  background-color: rgba(0, 128, 255, 0.1);
}

.variant-secondary.is-text {
  color: var(--secondary-color, #ff4081);
}
.variant-secondary.is-text:hover:not(:disabled) {
  background-color: rgba(255, 64, 129, 0.1);
}

.variant-success.is-text {
  color: var(--success-color, #4caf50);
}
.variant-success.is-text:hover:not(:disabled) {
  background-color: rgba(76, 175, 80, 0.1);
}

.variant-danger.is-text {
  color: var(--error-color, #f44336);
}
.variant-danger.is-text:hover:not(:disabled) {
  background-color: rgba(244, 67, 54, 0.1);
}

.variant-warning.is-text {
  color: var(--warning-color, #ff9800);
}
.variant-warning.is-text:hover:not(:disabled) {
  background-color: rgba(255, 152, 0, 0.1);
}

.variant-info.is-text {
  color: var(--info-color, #2196f3);
}
.variant-info.is-text:hover:not(:disabled) {
  background-color: rgba(33, 150, 243, 0.1);
}

.variant-neutral.is-text {
  color: #757575;
}
.variant-neutral.is-text:hover:not(:disabled) {
  background-color: rgba(0, 0, 0, 0.05);
}

/* Icon styling */
.button-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.button-icon {
  display: inline-flex;
}

.button-icon-left {
  margin-right: 0.5rem;
}

.button-icon-right {
  margin-left: 0.5rem;
}

.is-icon-only {
  padding: 0.5rem;
}

.size-small.is-icon-only {
  padding: 0.25rem;
}

.size-large.is-icon-only {
  padding: 0.75rem;
}

/* Disabled state */
.custom-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* Loading state */
.is-loading {
  position: relative;
}

.button-loader {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.invisible {
  visibility: hidden;
}

.loader-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
  margin: 0 2px;
  animation: pulse 1.2s infinite;
  opacity: 0.65;
}

.loader-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.loader-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(0.75);
    opacity: 0.65;
  }
  50% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Focus state */
.custom-button:focus-visible {
  box-shadow: 0 0 0 3px rgba(0, 128, 255, 0.4);
  outline: none;
}
</style>
