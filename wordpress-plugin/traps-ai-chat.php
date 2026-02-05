<?php
/**
 * Plugin Name: UITraps AI Chat
 * Plugin URI: https://uitraps.com
 * Description: AI chat assistant for paid subscribers using pre-indexed content
 * Version: 1.0.0
 * Author: UITraps
 * Author URI: https://uitraps.com
 * License: Proprietary
 * Requires PHP: 7.4
 * Requires at least: 6.0
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('TRAPS_AI_VERSION', '1.0.0');
define('TRAPS_AI_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('TRAPS_AI_PLUGIN_URL', plugin_dir_url(__FILE__));

// Configuration (can be overridden in wp-config.php)
if (!defined('TRAPS_AI_API_URL')) {
    define('TRAPS_AI_API_URL', ''); // Set in wp-config.php or plugin settings
}

if (!defined('TRAPS_AI_JWT_SECRET')) {
    define('TRAPS_AI_JWT_SECRET', ''); // MUST be set in wp-config.php
}

/**
 * Main plugin class
 */
class Traps_AI_Chat {

    private static $instance = null;

    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('plugins_loaded', array($this, 'init'));
    }

    public function init() {
        // Register shortcode
        add_shortcode('traps_ai_chat', array($this, 'render_chat_shortcode'));

        // Enqueue scripts and styles
        add_action('wp_enqueue_scripts', array($this, 'enqueue_assets'));

        // Register AJAX endpoints
        add_action('wp_ajax_traps_ai_get_token', array($this, 'ajax_get_token'));
        add_action('wp_ajax_nopriv_traps_ai_get_token', array($this, 'ajax_get_token'));

        // Add settings page
        if (is_admin()) {
            add_action('admin_menu', array($this, 'add_admin_menu'));
            add_action('admin_init', array($this, 'register_settings'));
        }
    }

    /**
     * Check if user has active subscription
     */
    private function has_active_subscription($user_id) {
        if (!$user_id) {
            return false;
        }

        // Option 1: Check user meta (if using custom subscription system)
        $subscription_active = get_user_meta($user_id, 'subscription_active', true);

        // Option 2: Check user role (common approach)
        $user = get_userdata($user_id);
        if (!$user) {
            return false;
        }

        $allowed_roles = array('subscriber', 'contributor', 'author', 'editor', 'administrator');
        $has_role = array_intersect($allowed_roles, $user->roles);

        // Option 3: If using WooCommerce Subscriptions
        // if (function_exists('wcs_user_has_subscription')) {
        //     return wcs_user_has_subscription($user_id, '', 'active');
        // }

        // Option 4: If using MemberPress
        // if (class_exists('MeprUser')) {
        //     $mepr_user = new MeprUser($user_id);
        //     return $mepr_user->is_active();
        // }

        // Default: check if user is logged in and has allowed role
        return !empty($has_role);
    }

    /**
     * Generate JWT token for authenticated API requests
     */
    private function generate_jwt($user_id) {
        if (empty(TRAPS_AI_JWT_SECRET)) {
            return new WP_Error('config_error', 'JWT secret not configured');
        }

        $issued_at = time();
        $expiration = $issued_at + 3600; // 1 hour

        $payload = array(
            'userId' => $user_id,
            'hasActiveSubscription' => $this->has_active_subscription($user_id),
            'iat' => $issued_at,
            'exp' => $expiration,
        );

        return $this->encode_jwt($payload, TRAPS_AI_JWT_SECRET);
    }

    /**
     * Simple JWT encoding (HS256)
     */
    private function encode_jwt($payload, $secret) {
        $header = json_encode(array('typ' => 'JWT', 'alg' => 'HS256'));

        $base64_header = $this->base64url_encode($header);
        $base64_payload = $this->base64url_encode(json_encode($payload));

        $signature = hash_hmac('sha256', "$base64_header.$base64_payload", $secret, true);
        $base64_signature = $this->base64url_encode($signature);

        return "$base64_header.$base64_payload.$base64_signature";
    }

    private function base64url_encode($data) {
        return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
    }

    /**
     * AJAX handler to get JWT token
     */
    public function ajax_get_token() {
        // Check if user is logged in
        if (!is_user_logged_in()) {
            wp_send_json_error(array(
                'message' => 'You must be logged in to use the AI assistant.'
            ), 401);
        }

        $user_id = get_current_user_id();

        // Check if user has active subscription
        if (!$this->has_active_subscription($user_id)) {
            wp_send_json_error(array(
                'message' => 'An active subscription is required to use the AI assistant.'
            ), 403);
        }

        // Generate JWT token
        $token = $this->generate_jwt($user_id);

        if (is_wp_error($token)) {
            wp_send_json_error(array(
                'message' => $token->get_error_message()
            ), 500);
        }

        wp_send_json_success(array(
            'token' => $token,
            'apiUrl' => get_option('traps_ai_api_url', TRAPS_AI_API_URL)
        ));
    }

    /**
     * Enqueue frontend assets
     */
    public function enqueue_assets() {
        if (!is_singular() && !is_page()) {
            return;
        }

        wp_enqueue_style(
            'traps-ai-chat',
            TRAPS_AI_PLUGIN_URL . 'assets/chat.css',
            array(),
            TRAPS_AI_VERSION
        );

        wp_enqueue_script(
            'traps-ai-chat',
            TRAPS_AI_PLUGIN_URL . 'assets/chat.js',
            array(),
            TRAPS_AI_VERSION,
            true
        );

        wp_localize_script('traps-ai-chat', 'trapsAI', array(
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('traps_ai_nonce'),
            'isLoggedIn' => is_user_logged_in(),
            'hasSubscription' => $this->has_active_subscription(get_current_user_id()),
        ));
    }

    /**
     * Render chat shortcode
     */
    public function render_chat_shortcode($atts) {
        $atts = shortcode_atts(array(
            'title' => 'AI Assistant',
            'placeholder' => 'Ask a question about UITraps content...',
        ), $atts);

        ob_start();
        include TRAPS_AI_PLUGIN_DIR . 'templates/chat.php';
        return ob_get_clean();
    }

    /**
     * Add admin menu
     */
    public function add_admin_menu() {
        add_options_page(
            'UITraps AI Chat Settings',
            'AI Chat',
            'manage_options',
            'traps-ai-chat',
            array($this, 'render_settings_page')
        );
    }

    /**
     * Register settings
     */
    public function register_settings() {
        register_setting('traps_ai_settings', 'traps_ai_api_url');

        add_settings_section(
            'traps_ai_main_section',
            'API Configuration',
            array($this, 'render_section_info'),
            'traps-ai-chat'
        );

        add_settings_field(
            'traps_ai_api_url',
            'Backend API URL',
            array($this, 'render_api_url_field'),
            'traps-ai-chat',
            'traps_ai_main_section'
        );
    }

    public function render_section_info() {
        echo '<p>Configure the backend API endpoint for the AI assistant.</p>';
    }

    public function render_api_url_field() {
        $value = get_option('traps_ai_api_url', TRAPS_AI_API_URL);
        echo '<input type="url" name="traps_ai_api_url" value="' . esc_attr($value) . '" class="regular-text" placeholder="https://your-api.vercel.app">';
        echo '<p class="description">Your backend API endpoint URL (e.g., https://api.uitraps.com)</p>';
    }

    /**
     * Render settings page
     */
    public function render_settings_page() {
        if (!current_user_can('manage_options')) {
            return;
        }
        ?>
        <div class="wrap">
            <h1>UITraps AI Chat Settings</h1>

            <?php if (empty(TRAPS_AI_JWT_SECRET)): ?>
                <div class="notice notice-error">
                    <p><strong>Configuration Error:</strong> JWT secret not set. Add this to your wp-config.php:</p>
                    <code>define('TRAPS_AI_JWT_SECRET', 'your-random-secret-here');</code>
                </div>
            <?php endif; ?>

            <form method="post" action="options.php">
                <?php
                settings_fields('traps_ai_settings');
                do_settings_sections('traps-ai-chat');
                submit_button();
                ?>
            </form>

            <hr>

            <h2>Usage</h2>
            <p>Add the chat interface to any page or post using this shortcode:</p>
            <code>[traps_ai_chat]</code>

            <h2>Requirements</h2>
            <ul style="list-style: disc; margin-left: 20px;">
                <li>Backend API must be deployed and accessible</li>
                <li>JWT secret must match between WordPress and backend</li>
                <li>Users must be logged in with active subscription</li>
            </ul>
        </div>
        <?php
    }
}

// Initialize plugin
Traps_AI_Chat::get_instance();
