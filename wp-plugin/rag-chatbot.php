<?php
/**
 * Plugin Name: RAG Chatbot
 * Description: [rag_chatbot] shortcode that asks a Python RAG backend about your site content.
 * Version: 0.1.0
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

function ragbot_ask( WP_REST_Request $req ) {
	$backend = get_option( 'ragbot_backend', 'http://127.0.0.1:8000' );
	$res     = wp_remote_post( trailingslashit( $backend ) . 'ask', array(
		'headers' => array( 'Content-Type' => 'application/json' ),
		'body'    => wp_json_encode( array( 'question' => sanitize_text_field( $req['q'] ) ) ),
		'timeout' => 20,
	) );
	if ( is_wp_error( $res ) ) {
		return new WP_REST_Response( array( 'answer' => 'Backend unavailable.' ), 502 );
	}
	return json_decode( wp_remote_retrieve_body( $res ), true );
}

add_action( 'rest_api_init', function () {
	register_rest_route( 'ragbot/v1', '/ask', array(
		'methods'             => 'GET',
		'callback'            => 'ragbot_ask',
		'permission_callback' => '__return_true',
	) );
} );

add_shortcode( 'rag_chatbot', function () {
	$url = esc_url( rest_url( 'ragbot/v1/ask' ) );
	return '<div id="ragbot"><input id="ragbot-q" placeholder="Ask about this site"><button id="ragbot-go">Ask</button><p id="ragbot-a"></p></div>'
		. '<script>document.getElementById("ragbot-go").onclick=async()=>{const q=document.getElementById("ragbot-q").value;'
		. 'const r=await fetch("' . $url . '?q="+encodeURIComponent(q));const j=await r.json();'
		. 'document.getElementById("ragbot-a").textContent=j.answer||"No answer";};</script>';
} );
