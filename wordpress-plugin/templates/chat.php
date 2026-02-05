<!-- UITraps AI Chat Interface -->
<div class="traps-ai-chat-container" id="traps-ai-chat">

    <!-- Chat Header -->
    <div class="traps-ai-header">
        <h3><?php echo esc_html($atts['title']); ?></h3>
        <button class="traps-ai-minimize" aria-label="Minimize chat">−</button>
    </div>

    <!-- Chat Messages -->
    <div class="traps-ai-messages" id="traps-ai-messages">
        <div class="traps-ai-message traps-ai-assistant">
            <div class="traps-ai-avatar">🤖</div>
            <div class="traps-ai-content">
                <p>Hello! I'm your UITraps AI assistant. I can answer questions about design patterns, UI traps, and best practices from the UITraps content library.</p>
                <p>What would you like to know?</p>
            </div>
        </div>
    </div>

    <!-- Loading Indicator -->
    <div class="traps-ai-loading" id="traps-ai-loading" style="display: none;">
        <span class="traps-ai-dot"></span>
        <span class="traps-ai-dot"></span>
        <span class="traps-ai-dot"></span>
    </div>

    <!-- Input Area -->
    <div class="traps-ai-input-area">
        <textarea
            id="traps-ai-input"
            placeholder="<?php echo esc_attr($atts['placeholder']); ?>"
            rows="1"
            maxlength="2000"
        ></textarea>
        <button id="traps-ai-send" class="traps-ai-send-btn">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 10L18 2L12 18L10 11L2 10Z"/>
            </svg>
        </button>
    </div>

    <!-- Error Display -->
    <div class="traps-ai-error" id="traps-ai-error" style="display: none;"></div>
</div>
