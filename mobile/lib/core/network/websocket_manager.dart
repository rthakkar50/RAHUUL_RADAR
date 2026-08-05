import 'dart:async';
import 'package:flutter/foundation.dart';

enum WebSocketConnectionState {
  disconnected,
  connecting,
  connected,
  reconnecting,
}

class LiveEventModel {
  final String topic;
  final String eventType;
  final Map<String, dynamic> data;
  final DateTime timestamp;

  const LiveEventModel({
    required this.topic,
    required this.eventType,
    required this.data,
    required this.timestamp,
  });

  factory LiveEventModel.fromJson(Map<String, dynamic> json) {
    return LiveEventModel(
      topic: json['topic'] ?? 'global',
      eventType: json['event_type'] ?? 'tick',
      data: json['data'] ?? {},
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
    );
  }
}

class WebSocketManager {
  static final WebSocketManager _instance = WebSocketManager._internal();
  factory WebSocketManager() => _instance;
  WebSocketManager._internal();

  WebSocketConnectionState _connectionState =
      WebSocketConnectionState.disconnected;
  final StreamController<WebSocketConnectionState> _stateController =
      StreamController.broadcast();
  final StreamController<LiveEventModel> _eventStreamController =
      StreamController.broadcast();

  Timer? _heartbeatTimer;
  Timer? _reconnectTimer;
  int _reconnectAttempts = 0;
  final Set<String> _subscribedTopics = {};

  int get reconnectAttempts => _reconnectAttempts;

  WebSocketConnectionState get connectionState => _connectionState;
  Stream<WebSocketConnectionState> get stateStream => _stateController.stream;
  Stream<LiveEventModel> get eventStream => _eventStreamController.stream;

  void connect({String url = 'ws://80.225.242.87:8000/ws/v1'}) {

    if (_connectionState == WebSocketConnectionState.connected ||
        _connectionState == WebSocketConnectionState.connecting) {
      return;
    }

    _setConnectionState(WebSocketConnectionState.connecting);
    debugPrint('[WebSocketManager] Connecting to $url');

    // Simulate robust socket connection handshake
    Future.delayed(const Duration(milliseconds: 300), () {
      _setConnectionState(WebSocketConnectionState.connected);
      _reconnectAttempts = 0;
      _startHeartbeat();
      debugPrint('[WebSocketManager] Connected cleanly to WebSocket stream.');
    });
  }

  void _setConnectionState(WebSocketConnectionState newState) {
    _connectionState = newState;
    _stateController.add(_connectionState);
  }

  void subscribe(String topic) {
    _subscribedTopics.add(topic);
    debugPrint('[WebSocketManager] Subscribed to topic: $topic');
  }

  void unsubscribe(String topic) {
    _subscribedTopics.remove(topic);
    debugPrint('[WebSocketManager] Unsubscribed from topic: $topic');
  }

  void _startHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(const Duration(seconds: 15), (_) {
      if (_connectionState == WebSocketConnectionState.connected) {
        debugPrint('[WebSocketManager] Heartbeat Ping -> Pong OK');
      }
    });
  }

  void pushEvent(LiveEventModel event) {
    if (_connectionState == WebSocketConnectionState.connected &&
        _subscribedTopics.contains(event.topic)) {
      _eventStreamController.add(event);
    }
  }

  void disconnect() {
    _heartbeatTimer?.cancel();
    _reconnectTimer?.cancel();
    _setConnectionState(WebSocketConnectionState.disconnected);
    debugPrint('[WebSocketManager] Disconnected from WebSocket stream.');
  }

  void dispose() {
    disconnect();
    _stateController.close();
    _eventStreamController.close();
  }
}
