"""
Enhanced Decentralized Cloud Storage Network Simulation
Implements all requested features:
- Real storage capacity with finite space
- Contract duration with dynamic space release
- Simulated network latency
- Simple reputation system
- Monte Carlo metrics collection
"""

import asyncio
import random
import time
import json
import logging
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EnhancedCloudStorageSim")

@dataclass
class StorageRequest:
    """Storage request data structure"""
    buyer_id: str
    space_gb: int
    duration_hours: float
    max_price_per_gb_hour: float
    timestamp: float
    request_id: str

@dataclass
class StorageContract:
    """Storage contract data structure"""
    contract_id: str
    buyer_id: str
    provider_id: str
    space_gb: int
    duration_hours: float
    price_per_gb_hour: float
    total_cost: float
    start_time: float
    end_time: float
    status: str  # 'pending', 'active', 'completed', 'failed'

@dataclass
class ProviderInfo:
    """Provider information maintained by the network"""
    agent_id: str
    total_space_gb: int
    available_space_gb: int
    reputation: float
    price_per_gb_hour: float
    last_seen: float
    success_count: int
    failure_count: int
    response_time_avg: float

class SimulationMetrics:
    """Enhanced metrics collection for Monte Carlo analysis"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all metrics for new simulation run"""
        self.start_time = time.time()
        
        # Request metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = []
        
        # Contract metrics
        self.contracts_created = 0
        self.contracts_completed = 0
        self.contracts_failed = 0
        self.contract_durations = []
        self.contract_values = []
        
        # Provider metrics
        self.provider_utilizations = []
        self.provider_reputations = []
        self.provider_earnings = []
        
        # Network metrics
        self.network_corruptions = 0
        self.provider_failures = 0
        self.network_latencies = []
        
        # System metrics
        self.total_space_allocated = 0
        self.peak_utilization = 0.0
        self.avg_utilization = 0.0
        
    def record_request(self, successful: bool, response_time: float = 0):
        """Record a storage request"""
        self.total_requests += 1
        if successful:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        if response_time > 0:
            self.response_times.append(response_time)
    
    def record_contract(self, contract: StorageContract, completed: bool = False):
        """Record contract information"""
        if contract.status == 'active':
            self.contracts_created += 1
            self.contract_durations.append(contract.duration_hours)
            self.contract_values.append(contract.total_cost)
        elif completed:
            self.contracts_completed += 1
    
    def record_provider_metrics(self, utilization: float, reputation: float, earnings: float = 0):
        """Record provider metrics"""
        self.provider_utilizations.append(utilization)
        self.provider_reputations.append(reputation)
        if earnings > 0:
            self.provider_earnings.append(earnings)
    
    def record_network_event(self, event_type: str, latency: float = 0):
        """Record network events"""
        if event_type == 'corruption':
            self.network_corruptions += 1
        elif event_type == 'provider_failure':
            self.provider_failures += 1
        
        if latency > 0:
            self.network_latencies.append(latency)
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate comprehensive simulation summary"""
        simulation_duration = time.time() - self.start_time
        
        # Calculate success rate
        success_rate = (self.successful_requests / max(self.total_requests, 1)) * 100
        
        # Calculate average metrics
        avg_response_time = statistics.mean(self.response_times) if self.response_times else 0
        std_response_time = statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0
        
        avg_contract_duration = statistics.mean(self.contract_durations) if self.contract_durations else 0
        avg_contract_value = statistics.mean(self.contract_values) if self.contract_values else 0
        
        avg_utilization = statistics.mean(self.provider_utilizations) if self.provider_utilizations else 0
        avg_reputation = statistics.mean(self.provider_reputations) if self.provider_reputations else 0
        
        total_earnings = sum(self.provider_earnings) if self.provider_earnings else 0
        avg_network_latency = statistics.mean(self.network_latencies) if self.network_latencies else 0
        
        return {
            'simulation_duration': simulation_duration,
            'requests': {
                'total': self.total_requests,
                'successful': self.successful_requests,
                'failed': self.failed_requests,
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'std_response_time': std_response_time
            },
            'contracts': {
                'created': self.contracts_created,
                'completed': self.contracts_completed,
                'failed': self.contracts_failed,
                'avg_duration_hours': avg_contract_duration,
                'avg_value': avg_contract_value,
                'completion_rate': (self.contracts_completed / max(self.contracts_created, 1)) * 100
            },
            'providers': {
                'avg_utilization': avg_utilization,
                'avg_reputation': avg_reputation,
                'total_earnings': total_earnings,
                'avg_earnings_per_provider': total_earnings / 3 if total_earnings > 0 else 0  # Assuming 3 providers
            },
            'network': {
                'corruptions': self.network_corruptions,
                'provider_failures': self.provider_failures,
                'avg_latency': avg_network_latency,
                'corruption_rate': (self.network_corruptions / max(self.total_requests, 1)) * 100
            }
        }

# Global metrics instance
global_metrics = SimulationMetrics()

class MessageBus:
    """Enhanced message bus with network latency simulation"""
    
    def __init__(self):
        self.mailboxes = {}
        self.message_count = 0
    
    def register_agent(self, agent_id: str):
        """Register an agent with the message bus"""
        self.mailboxes[agent_id] = asyncio.Queue()
        logger.debug(f"Registered agent {agent_id}")
    
    async def send_message(self, from_agent: str, to_agent: str, message: Dict[str, Any], 
                          simulate_latency: bool = True):
        """Send message with optional network latency simulation"""
        if to_agent not in self.mailboxes:
            logger.warning(f"Agent {to_agent} not registered")
            return False
        
        # Simulate network latency
        latency = 0
        if simulate_latency:
            latency = random.uniform(0.05, 0.5)  # 50ms to 500ms
            await asyncio.sleep(latency)
            global_metrics.record_network_event('latency', latency)
        
        # Create message envelope
        msg_envelope = {
            'from': from_agent,
            'to': to_agent,
            'body': message,
            'timestamp': time.time(),
            'latency': latency,
            'id': self.message_count
        }
        
        self.message_count += 1
        
        try:
            await self.mailboxes[to_agent].put(msg_envelope)
            return True
        except Exception as e:
            logger.error(f"Failed to send message from {from_agent} to {to_agent}: {e}")
            return False
    
    async def receive_message(self, agent_id: str, timeout: float = 10.0):
        """Receive message with timeout"""
        try:
            return await asyncio.wait_for(self.mailboxes[agent_id].get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

class BuyerAgent:
    """Enhanced buyer agent with dynamic pricing and preferences"""
    
    def __init__(self, agent_id: str, broker_id: str, message_bus: MessageBus, 
                 request_interval: Tuple[float, float] = (3.0, 8.0),
                 budget_per_hour: float = 10.0):
        self.agent_id = agent_id
        self.broker_id = broker_id
        self.message_bus = message_bus
        self.request_interval = request_interval
        self.budget_per_hour = budget_per_hour
        
        # State tracking
        self.pending_requests = {}
        self.active_contracts = {}
        self.completed_contracts = []
        self.running = False
        
        # Enhanced statistics
        self.stats = {
            'requests_sent': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'total_spent': 0.0,
            'total_storage_used': 0,
            'avg_response_time': 0.0,
            'contracts_completed': 0
        }
        
        message_bus.register_agent(agent_id)
    
    async def start(self):
        """Start buyer agent behaviors"""
        self.running = True
        
        # Start request generation
        asyncio.create_task(self.request_behavior())
        
        # Start response handling
        asyncio.create_task(self.response_handler())
        
        logger.info(f"🛒 Buyer {self.agent_id} started with budget ${self.budget_per_hour:.2f}/hour")
    
    async def stop(self):
        """Stop buyer agent"""
        self.running = False
        logger.info(f"🛒 Buyer {self.agent_id} stopped")
    
    async def request_behavior(self):
        """Generate storage requests periodically"""
        while self.running:
            try:
                # Generate request parameters
                space_needed = random.randint(5, 50)  # 5-50 GB
                duration = random.uniform(0.5, 6.0)   # 0.5-6 hours
                max_price = min(
                    random.uniform(0.2, 1.5),  # $0.2-1.5 per GB/hour
                    self.budget_per_hour / space_needed  # Budget constraint
                )
                
                request_id = f"REQ-{self.agent_id}-{int(time.time())}-{random.randint(100, 999)}"
                
                request = StorageRequest(
                    buyer_id=self.agent_id,
                    space_gb=space_needed,
                    duration_hours=duration,
                    max_price_per_gb_hour=max_price,
                    timestamp=time.time(),
                    request_id=request_id
                )
                
                # Store pending request
                self.pending_requests[request_id] = request
                
                # Send to broker
                message = {
                    'type': 'storage_request',
                    'request': asdict(request)
                }
                
                success = await self.message_bus.send_message(
                    self.agent_id, self.broker_id, message
                )
                
                if success:
                    self.stats['requests_sent'] += 1
                    global_metrics.record_request(False)  # Will be updated when response received
                    
                    logger.info(f"🛒 {self.agent_id} requested {space_needed}GB for {duration:.1f}h "
                              f"at max ${max_price:.3f}/GB/h")
                else:
                    logger.error(f"Failed to send request {request_id}")
                
                # Wait for next request
                wait_time = random.uniform(*self.request_interval)
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"Error in buyer request behavior: {e}")
                await asyncio.sleep(1)
    
    async def response_handler(self):
        """Handle responses from the broker"""
        while self.running:
            try:
                msg = await self.message_bus.receive_message(self.agent_id, timeout=1.0)
                if msg:
                    await self.process_response(msg)
            except Exception as e:
                logger.error(f"Error in buyer response handler: {e}")
                await asyncio.sleep(0.1)
    
    async def process_response(self, msg: Dict[str, Any]):
        """Process response message"""
        try:
            message_body = msg['body']
            msg_type = message_body.get('type')
            
            if msg_type == 'storage_response':
                response = message_body['response']
                request_id = response['request_id']
                
                if request_id in self.pending_requests:
                    original_request = self.pending_requests[request_id]
                    response_time = time.time() - original_request.timestamp
                    
                    if response['status'] == 'success':
                        # Successful allocation
                        contract = StorageContract(**response['contract'])
                        self.active_contracts[contract.contract_id] = contract
                        
                        self.stats['requests_successful'] += 1
                        self.stats['total_spent'] += contract.total_cost
                        self.stats['total_storage_used'] += contract.space_gb
                        
                        global_metrics.record_request(True, response_time)
                        global_metrics.record_contract(contract)
                        
                        # Schedule contract completion tracking
                        asyncio.create_task(self.track_contract_completion(contract))
                        
                        logger.info(f"✅ {self.agent_id} contract {contract.contract_id} accepted - "
                                  f"Cost: ${contract.total_cost:.2f}, Duration: {contract.duration_hours:.1f}h")
                    else:
                        # Request rejected
                        self.stats['requests_failed'] += 1
                        reason = response.get('reason', 'unknown')
                        
                        global_metrics.record_request(False, response_time)
                        
                        logger.info(f"❌ {self.agent_id} request {request_id} rejected: {reason}")
                    
                    # Update average response time
                    total_responses = self.stats['requests_successful'] + self.stats['requests_failed']
                    if total_responses > 0:
                        self.stats['avg_response_time'] = (
                            (self.stats['avg_response_time'] * (total_responses - 1) + response_time) 
                            / total_responses
                        )
                    
                    # Remove from pending
                    del self.pending_requests[request_id]
        
        except Exception as e:
            logger.error(f"Error processing response: {e}")
    
    async def track_contract_completion(self, contract: StorageContract):
        """Track when a contract completes"""
        try:
            # Wait for contract to complete
            wait_time = contract.end_time - time.time()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            
            # Mark as completed
            if contract.contract_id in self.active_contracts:
                del self.active_contracts[contract.contract_id]
                self.completed_contracts.append(contract)
                self.stats['contracts_completed'] += 1
                
                global_metrics.record_contract(contract, completed=True)
                
                logger.info(f"📦 {self.agent_id} contract {contract.contract_id} completed")
        
        except Exception as e:
            logger.error(f"Error tracking contract completion: {e}")

class StorageProviderAgent:
    """Enhanced storage provider with dynamic pricing and reputation"""
    
    def __init__(self, agent_id: str, broker_id: str, message_bus: MessageBus,
                 total_space_gb: int, base_price_per_gb_hour: float = 0.5,
                 failure_probability: float = 0.1):
        self.agent_id = agent_id
        self.broker_id = broker_id
        self.message_bus = message_bus
        self.total_space_gb = total_space_gb
        self.available_space_gb = total_space_gb
        self.base_price_per_gb_hour = base_price_per_gb_hour
        self.failure_probability = failure_probability
        
        # Dynamic pricing based on utilization
        self.current_price_per_gb_hour = base_price_per_gb_hour
        
        # Contract management
        self.active_contracts = {}
        self.completed_contracts = []
        
        # Reputation system
        self.reputation = 5.0  # Start with neutral reputation
        self.success_count = 0
        self.failure_count = 0
        
        # Statistics
        self.stats = {
            'requests_received': 0,
            'requests_accepted': 0,
            'requests_rejected': 0,
            'total_earnings': 0.0,
            'uptime': 0.0,
            'avg_utilization': 0.0,
            'contracts_completed': 0,
            'current_reputation': self.reputation
        }
        
        self.start_time = time.time()
        self.running = False
        
        message_bus.register_agent(agent_id)
    
    async def start(self):
        """Start provider agent behaviors"""
        self.running = True
        
        # Register with broker
        await self.register_with_broker()
        
        # Start request handling
        asyncio.create_task(self.request_handler())
        
        # Start contract management
        asyncio.create_task(self.contract_manager())
        
        # Start status updates
        asyncio.create_task(self.status_updater())
        
        # Start dynamic pricing
        asyncio.create_task(self.dynamic_pricing())
        
        logger.info(f"💾 Provider {self.agent_id} started: {self.total_space_gb}GB at "
                   f"${self.current_price_per_gb_hour:.3f}/GB/h")
    
    async def stop(self):
        """Stop provider agent"""
        self.running = False
        logger.info(f"💾 Provider {self.agent_id} stopped")
    
    async def register_with_broker(self):
        """Register provider capabilities with broker"""
        provider_info = ProviderInfo(
            agent_id=self.agent_id,
            total_space_gb=self.total_space_gb,
            available_space_gb=self.available_space_gb,
            reputation=self.reputation,
            price_per_gb_hour=self.current_price_per_gb_hour,
            last_seen=time.time(),
            success_count=self.success_count,
            failure_count=self.failure_count,
            response_time_avg=0.1
        )
        
        message = {
            'type': 'provider_registration',
            'provider_info': asdict(provider_info)
        }
        
        await self.message_bus.send_message(self.agent_id, self.broker_id, message)
        logger.debug(f"Provider {self.agent_id} registered with broker")
    
    async def request_handler(self):
        """Handle allocation requests from broker"""
        while self.running:
            try:
                msg = await self.message_bus.receive_message(self.agent_id, timeout=1.0)
                if msg:
                    await self.process_allocation_request(msg)
            except Exception as e:
                logger.error(f"Error in provider request handler: {e}")
                await asyncio.sleep(0.1)
    
    async def process_allocation_request(self, msg: Dict[str, Any]):
        """Process allocation request"""
        try:
            message_body = msg['body']
            
            if message_body.get('type') == 'allocation_request':
                contract_data = message_body['contract']
                request_id = message_body['request_id']
                
                self.stats['requests_received'] += 1
                
                # Simulate processing time
                await asyncio.sleep(random.uniform(0.05, 0.2))
                
                # Decision making
                space_needed = contract_data['space_gb']
                can_allocate = self.can_fulfill_request(space_needed)
                
                if can_allocate:
                    # Accept contract
                    contract = StorageContract(**contract_data)
                    self.active_contracts[contract.contract_id] = contract
                    self.available_space_gb -= space_needed
                    self.stats['requests_accepted'] += 1
                    self.stats['total_earnings'] += contract.total_cost
                    
                    # Update reputation for acceptance
                    self.update_reputation(True)
                    
                    response = {
                        'type': 'allocation_response',
                        'request_id': request_id,
                        'contract_id': contract.contract_id,
                        'status': 'accepted',
                        'provider_id': self.agent_id
                    }
                    
                    logger.info(f"🟢 Provider {self.agent_id} accepted contract {contract.contract_id} "
                              f"({space_needed}GB, ${contract.total_cost:.2f})")
                else:
                    # Reject contract
                    self.stats['requests_rejected'] += 1
                    
                    # Update reputation for rejection
                    self.update_reputation(False)
                    global_metrics.record_network_event('provider_failure')
                    
                    reason = ('insufficient_space' if self.available_space_gb < space_needed 
                             else 'provider_failure')
                    
                    response = {
                        'type': 'allocation_response',
                        'request_id': request_id,
                        'status': 'rejected',
                        'reason': reason,
                        'provider_id': self.agent_id
                    }
                    
                    logger.info(f"🔴 Provider {self.agent_id} rejected request {request_id}: {reason}")
                
                # Send response
                await self.message_bus.send_message(self.agent_id, msg['from'], response)
        
        except Exception as e:
            logger.error(f"Error processing allocation request: {e}")
    
    def can_fulfill_request(self, space_needed: int) -> bool:
        """Determine if provider can fulfill request"""
        # Check space availability
        if self.available_space_gb < space_needed:
            return False
        
        # Simulate random failures
        if random.random() < self.failure_probability:
            return False
        
        return True
    
    def update_reputation(self, success: bool):
        """Update provider reputation based on performance"""
        if success:
            self.success_count += 1
            self.reputation = min(self.reputation * 1.02, 10.0)  # Gradual increase, max 10
        else:
            self.failure_count += 1
            self.reputation = max(self.reputation * 0.98, 0.1)  # Gradual decrease, min 0.1
        
        self.stats['current_reputation'] = self.reputation
        
        # Record metrics
        global_metrics.record_provider_metrics(
            self.get_utilization(), 
            self.reputation,
            self.stats['total_earnings']
        )
    
    def get_utilization(self) -> float:
        """Calculate current utilization"""
        return (self.total_space_gb - self.available_space_gb) / self.total_space_gb
    
    async def contract_manager(self):
        """Manage active contracts and release space when expired"""
        while self.running:
            try:
                current_time = time.time()
                completed_contracts = []
                
                for contract_id, contract in self.active_contracts.items():
                    if current_time >= contract.end_time:
                        # Release space
                        self.available_space_gb += contract.space_gb
                        self.stats['contracts_completed'] += 1
                        
                        # Move to completed
                        contract.status = 'completed'
                        self.completed_contracts.append(contract)
                        completed_contracts.append(contract_id)
                        
                        logger.info(f"📦 Provider {self.agent_id} completed contract {contract_id} "
                                  f"- Released {contract.space_gb}GB")
                
                # Remove completed contracts
                for contract_id in completed_contracts:
                    del self.active_contracts[contract_id]
                
                await asyncio.sleep(2)  # Check every 2 seconds
            
            except Exception as e:
                logger.error(f"Error in contract manager: {e}")
                await asyncio.sleep(1)
    
    async def status_updater(self):
        """Send periodic status updates to broker"""
        while self.running:
            try:
                # Update statistics
                self.stats['uptime'] = time.time() - self.start_time
                utilization = self.get_utilization()
                self.stats['avg_utilization'] = utilization
                
                # Send status update
                status = {
                    'type': 'status_update',
                    'provider_id': self.agent_id,
                    'available_space_gb': self.available_space_gb,
                    'utilization': utilization,
                    'reputation': self.reputation,
                    'price_per_gb_hour': self.current_price_per_gb_hour,
                    'active_contracts': len(self.active_contracts)
                }
                
                await self.message_bus.send_message(self.agent_id, self.broker_id, status)
                
                await asyncio.sleep(5)  # Update every 5 seconds
            
            except Exception as e:
                logger.error(f"Error in status updater: {e}")
                await asyncio.sleep(1)
    
    async def dynamic_pricing(self):
        """Adjust pricing based on utilization and demand"""
        while self.running:
            try:
                utilization = self.get_utilization()
                
                # Adjust price based on utilization
                if utilization > 0.8:  # High utilization
                    self.current_price_per_gb_hour = min(
                        self.base_price_per_gb_hour * 1.5, 
                        self.base_price_per_gb_hour * 2.0
                    )
                elif utilization < 0.3:  # Low utilization
                    self.current_price_per_gb_hour = max(
                        self.base_price_per_gb_hour * 0.8,
                        self.base_price_per_gb_hour * 0.5
                    )
                else:  # Normal utilization
                    self.current_price_per_gb_hour = self.base_price_per_gb_hour
                
                await asyncio.sleep(10)  # Adjust every 10 seconds
            
            except Exception as e:
                logger.error(f"Error in dynamic pricing: {e}")
                await asyncio.sleep(1)

class IntermediaryNetworkAgent:
    """Enhanced network broker with reputation-based provider selection"""
    
    def __init__(self, agent_id: str, message_bus: MessageBus, 
                 corruption_probability: float = 0.05):
        self.agent_id = agent_id
        self.message_bus = message_bus
        self.corruption_probability = corruption_probability
        
        # Provider management
        self.providers = {}  # provider_id -> ProviderInfo
        self.provider_last_seen = {}
        
        # Request tracking
        self.pending_allocations = {}  # request_id -> (buyer_id, request, selected_provider)
        
        # Statistics
        self.stats = {
            'requests_processed': 0,
            'successful_allocations': 0,
            'failed_allocations': 0,
            'corrupted_contracts': 0,
            'active_providers': 0,
            'total_providers_registered': 0,
            'avg_response_time': 0.0
        }
        
        self.running = False
        message_bus.register_agent(agent_id)
    
    async def start(self):
        """Start network agent behaviors"""
        self.running = True
        
        # Start message handling
        asyncio.create_task(self.message_handler())
        
        # Start provider management
        asyncio.create_task(self.provider_manager())
        
        logger.info(f"🏢 Network {self.agent_id} started")
    
    async def stop(self):
        """Stop network agent"""
        self.running = False
        logger.info(f"🏢 Network {self.agent_id} stopped")
    
    async def message_handler(self):
        """Handle all incoming messages"""
        while self.running:
            try:
                msg = await self.message_bus.receive_message(self.agent_id, timeout=1.0)
                if msg:
                    await self.process_message(msg)
            except Exception as e:
                logger.error(f"Error in network message handler: {e}")
                await asyncio.sleep(0.1)
    
    async def process_message(self, msg: Dict[str, Any]):
        """Process incoming message based on type"""
        try:
            message_body = msg['body']
            msg_type = message_body.get('type')
            
            if msg_type == 'provider_registration':
                await self.handle_provider_registration(msg)
            elif msg_type == 'storage_request':
                await self.handle_storage_request(msg)
            elif msg_type == 'allocation_response':
                await self.handle_allocation_response(msg)
            elif msg_type == 'status_update':
                await self.handle_status_update(msg)
            else:
                logger.warning(f"Unknown message type: {msg_type}")
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def handle_provider_registration(self, msg: Dict[str, Any]):
        """Handle provider registration"""
        try:
            provider_info = ProviderInfo(**msg['body']['provider_info'])
            self.providers[provider_info.agent_id] = provider_info
            self.provider_last_seen[provider_info.agent_id] = time.time()
            
            if provider_info.agent_id not in [p.agent_id for p in self.providers.values()]:
                self.stats['total_providers_registered'] += 1
            
            self.stats['active_providers'] = len(self.providers)
            
            logger.info(f"📋 Network registered provider {provider_info.agent_id}")
        
        except Exception as e:
            logger.error(f"Error handling provider registration: {e}")
    
    async def handle_storage_request(self, msg: Dict[str, Any]):
        """Handle storage request from buyer"""
        try:
            request = StorageRequest(**msg['body']['request'])
            buyer_id = msg['from']
            
            self.stats['requests_processed'] += 1
            
            logger.info(f"🏢 Network processing request {request.request_id} from {buyer_id}")
            
            # Select provider using reputation-based algorithm
            selected_provider = self.select_provider(request)
            
            if selected_provider:
                # Calculate contract details
                total_cost = (request.space_gb * request.duration_hours * 
                            selected_provider.price_per_gb_hour)
                
                contract = StorageContract(
                    contract_id=f"CONT-{int(time.time())}-{random.randint(1000, 9999)}",
                    buyer_id=request.buyer_id,
                    provider_id=selected_provider.agent_id,
                    space_gb=request.space_gb,
                    duration_hours=request.duration_hours,
                    price_per_gb_hour=selected_provider.price_per_gb_hour,
                    total_cost=total_cost,
                    start_time=time.time(),
                    end_time=time.time() + (request.duration_hours * 3600),
                    status='pending'
                )
                
                # Store pending allocation
                self.pending_allocations[request.request_id] = (buyer_id, request, selected_provider)
                
                # Send allocation request to provider
                allocation_message = {
                    'type': 'allocation_request',
                    'request_id': request.request_id,
                    'contract': asdict(contract)
                }
                
                await self.message_bus.send_message(
                    self.agent_id, selected_provider.agent_id, allocation_message
                )
                
                logger.info(f"🏢 Network forwarded request {request.request_id} to "
                          f"provider {selected_provider.agent_id}")
            else:
                # No suitable provider
                await self.send_failure_response(buyer_id, request.request_id, 
                                               "no_suitable_provider")
                self.stats['failed_allocations'] += 1
        
        except Exception as e:
            logger.error(f"Error handling storage request: {e}")
    
    def select_provider(self, request: StorageRequest) -> Optional[ProviderInfo]:
        """Select best provider using weighted reputation and capacity algorithm"""
        try:
            current_time = time.time()
            suitable_providers = []
            
            for provider in self.providers.values():
                # Check if provider meets requirements
                if (provider.available_space_gb >= request.space_gb and
                    provider.price_per_gb_hour <= request.max_price_per_gb_hour and
                    provider.reputation >= 1.0 and  # Minimum reputation
                    current_time - self.provider_last_seen.get(provider.agent_id, 0) < 30):
                    suitable_providers.append(provider)
            
            if not suitable_providers:
                return None
            
            # Score providers based on multiple factors
            def calculate_score(provider: ProviderInfo) -> float:
                # Reputation weight (40%)
                reputation_score = (provider.reputation / 10.0) * 0.4
                
                # Price weight (30%) - lower price is better
                max_price = request.max_price_per_gb_hour
                price_score = (1.0 - (provider.price_per_gb_hour / max_price)) * 0.3
                
                # Availability weight (20%) - more available space is better
                availability_score = (provider.available_space_gb / provider.total_space_gb) * 0.2
                
                # Success rate weight (10%)
                total_attempts = provider.success_count + provider.failure_count
                success_rate = (provider.success_count / max(total_attempts, 1)) * 0.1
                
                return reputation_score + price_score + availability_score + success_rate
            
            # Select provider with highest score
            suitable_providers.sort(key=calculate_score, reverse=True)
            return suitable_providers[0]
        
        except Exception as e:
            logger.error(f"Error selecting provider: {e}")
            return None
    
    async def handle_allocation_response(self, msg: Dict[str, Any]):
        """Handle allocation response from provider"""
        try:
            response = msg['body']
            request_id = response['request_id']
            
            if request_id in self.pending_allocations:
                buyer_id, original_request, selected_provider = self.pending_allocations[request_id]
                
                # Calculate response time
                response_time = time.time() - original_request.timestamp
                
                if response['status'] == 'accepted':
                    # Update provider reputation for success
                    if selected_provider.agent_id in self.providers:
                        provider = self.providers[selected_provider.agent_id]
                        provider.success_count += 1
                        provider.reputation = min(provider.reputation * 1.01, 10.0)
                    
                    # Check for contract corruption
                    corrupted = random.random() < self.corruption_probability
                    if corrupted:
                        self.stats['corrupted_contracts'] += 1
                        global_metrics.record_network_event('corruption')
                        
                        final_response = {
                            'type': 'storage_response',
                            'response': {
                                'request_id': request_id,
                                'status': 'failure',
                                'reason': 'network_corruption'
                            }
                        }
                        
                        logger.warning(f"⚠️ Network corrupted contract for request {request_id}")
                    else:
                        contract_data = {
                            'contract_id': response['contract_id'],
                            'buyer_id': original_request.buyer_id,
                            'provider_id': selected_provider.agent_id,
                            'space_gb': original_request.space_gb,
                            'duration_hours': original_request.duration_hours,
                            'price_per_gb_hour': selected_provider.price_per_gb_hour,
                            'total_cost': original_request.space_gb * original_request.duration_hours * selected_provider.price_per_gb_hour,
                            'start_time': time.time(),
                            'end_time': time.time() + (original_request.duration_hours * 3600),
                            'status': 'active'
                        }
                        
                        final_response = {
                            'type': 'storage_response',
                            'response': {
                                'request_id': request_id,
                                'status': 'success',
                                'contract': contract_data
                            }
                        }
                    
                    self.stats['successful_allocations'] += 1
                else:
                    # Update provider reputation for failure
                    if selected_provider.agent_id in self.providers:
                        provider = self.providers[selected_provider.agent_id]
                        provider.failure_count += 1
                        provider.reputation = max(provider.reputation * 0.99, 0.1)
                    
                    final_response = {
                        'type': 'storage_response',
                        'response': {
                            'request_id': request_id,
                            'status': 'failure',
                            'reason': response.get('reason', 'provider_rejected')
                        }
                    }
                    
                    self.stats['failed_allocations'] += 1
                
                # Send response to buyer
                await self.message_bus.send_message(self.agent_id, buyer_id, final_response)
                
                # Update average response time
                total_responses = self.stats['successful_allocations'] + self.stats['failed_allocations']
                if total_responses > 0:
                    self.stats['avg_response_time'] = (
                        (self.stats['avg_response_time'] * (total_responses - 1) + response_time)
                        / total_responses
                    )
                
                # Remove from pending
                del self.pending_allocations[request_id]
                
                logger.info(f"🏢 Network completed processing request {request_id} "
                          f"in {response_time:.2f}s")
        
        except Exception as e:
            logger.error(f"Error handling allocation response: {e}")
    
    async def send_failure_response(self, buyer_id: str, request_id: str, reason: str):
        """Send failure response to buyer"""
        try:
            response = {
                'type': 'storage_response',
                'response': {
                    'request_id': request_id,
                    'status': 'failure',
                    'reason': reason
                }
            }
            
            await self.message_bus.send_message(self.agent_id, buyer_id, response)
            logger.info(f"🏢 Network sent failure response for {request_id}: {reason}")
        
        except Exception as e:
            logger.error(f"Error sending failure response: {e}")
    
    async def handle_status_update(self, msg: Dict[str, Any]):
        """Handle status update from provider"""
        try:
            status = msg['body']
            provider_id = status['provider_id']
            
            if provider_id in self.providers:
                provider = self.providers[provider_id]
                provider.available_space_gb = status['available_space_gb']
                provider.reputation = status['reputation']
                provider.price_per_gb_hour = status['price_per_gb_hour']
                provider.last_seen = time.time()
                
                self.provider_last_seen[provider_id] = time.time()
        
        except Exception as e:
            logger.error(f"Error handling status update: {e}")
    
    async def provider_manager(self):
        """Manage provider lifecycle and cleanup"""
        while self.running:
            try:
                current_time = time.time()
                inactive_providers = []
                
                for provider_id, last_seen in self.provider_last_seen.items():
                    if current_time - last_seen > 60:  # 60 second timeout
                        inactive_providers.append(provider_id)
                
                for provider_id in inactive_providers:
                    if provider_id in self.providers:
                        del self.providers[provider_id]
                    del self.provider_last_seen[provider_id]
                    logger.info(f"🧹 Network removed inactive provider {provider_id}")
                
                self.stats['active_providers'] = len(self.providers)
                
                await asyncio.sleep(15)  # Check every 15 seconds
            
            except Exception as e:
                logger.error(f"Error in provider manager: {e}")
                await asyncio.sleep(1)

async def run_single_simulation(duration: int = 60, 
                               num_buyers: int = 2, 
                               num_providers: int = 3) -> Dict[str, Any]:
    """Run a single simulation iteration"""
    logger.info(f"🚀 Starting simulation: {duration}s, {num_buyers} buyers, {num_providers} providers")
    
    # Reset global metrics
    global_metrics.reset()
    
    # Create message bus
    message_bus = MessageBus()
    
    # Create network agent
    network = IntermediaryNetworkAgent("network", message_bus, corruption_probability=0.03)
    await network.start()
    
    # Create provider agents
    providers = []
    for i in range(num_providers):
        provider = StorageProviderAgent(
            agent_id=f"provider{i}",
            broker_id="network",
            message_bus=message_bus,
            total_space_gb=random.randint(100, 300),
            base_price_per_gb_hour=random.uniform(0.3, 0.9),
            failure_probability=random.uniform(0.02, 0.12)
        )
        providers.append(provider)
        await provider.start()
        await asyncio.sleep(0.5)  # Staggered startup
    
    # Create buyer agents
    buyers = []
    for i in range(num_buyers):
        buyer = BuyerAgent(
            agent_id=f"buyer{i}",
            broker_id="network",
            message_bus=message_bus,
            request_interval=(2.0, 8.0),
            budget_per_hour=random.uniform(15.0, 40.0)
        )
        buyers.append(buyer)
        await buyer.start()
        await asyncio.sleep(0.5)  # Staggered startup
    
    # Let simulation run
    logger.info(f"⏱️ Simulation running for {duration} seconds...")
    await asyncio.sleep(duration)
    
    # Stop all agents
    for agent in [network] + providers + buyers:
        await agent.stop()
    
    # Wait for final processing
    await asyncio.sleep(2)
    
    # Collect comprehensive metrics
    metrics = global_metrics.get_summary()
    
    # Add agent-specific statistics
    metrics['network_stats'] = network.stats
    metrics['provider_stats'] = [provider.stats for provider in providers]
    metrics['buyer_stats'] = [buyer.stats for buyer in buyers]
    
    # Calculate additional derived metrics
    total_provider_earnings = sum(p.stats['total_earnings'] for p in providers)
    total_buyer_spending = sum(b.stats['total_spent'] for b in buyers)
    
    metrics['economics'] = {
        'total_provider_earnings': total_provider_earnings,
        'total_buyer_spending': total_buyer_spending,
        'economic_efficiency': (total_provider_earnings / max(total_buyer_spending, 1)) * 100
    }
    
    return metrics

async def run_monte_carlo_simulation(iterations: int = 5, 
                                   duration_per_iteration: int = 45,
                                   num_buyers: int = 2,
                                   num_providers: int = 3):
    """Run Monte Carlo simulation with comprehensive analysis"""
    logger.info(f"🎯 Starting Monte Carlo simulation:")
    logger.info(f"   Iterations: {iterations}")
    logger.info(f"   Duration per iteration: {duration_per_iteration}s")
    logger.info(f"   Buyers: {num_buyers}, Providers: {num_providers}")
    
    all_results = []
    start_time = time.time()
    
    for i in range(iterations):
        logger.info(f"\n{'='*20} ITERATION {i+1}/{iterations} {'='*20}")
        
        try:
            # Run single simulation
            result = await run_single_simulation(
                duration=duration_per_iteration,
                num_buyers=num_buyers,
                num_providers=num_providers
            )
            
            all_results.append(result)
            
            # Log iteration summary
            logger.info(f"📊 Iteration {i+1} Summary:")
            logger.info(f"   Success Rate: {result['requests']['success_rate']:.1f}%")
            logger.info(f"   Avg Response Time: {result['requests']['avg_response_time']:.2f}s")
            logger.info(f"   Provider Utilization: {result['providers']['avg_utilization']:.2f}")
            logger.info(f"   Network Corruptions: {result['network']['corruptions']}")
            logger.info(f"   Economic Efficiency: {result['economics']['economic_efficiency']:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Error in iteration {i+1}: {e}")
            continue
        
        # Short break between iterations
        if i < iterations - 1:
            await asyncio.sleep(2)
    
    total_simulation_time = time.time() - start_time
    
    # Calculate comprehensive statistics
    if all_results:
        logger.info(f"\n{'='*20} MONTE CARLO RESULTS {'='*20}")
        
        # Extract key metrics
        success_rates = [r['requests']['success_rate'] for r in all_results]
        response_times = [r['requests']['avg_response_time'] for r in all_results]
        utilizations = [r['providers']['avg_utilization'] for r in all_results]
        corruptions = [r['network']['corruptions'] for r in all_results]
        economic_efficiencies = [r['economics']['economic_efficiency'] for r in all_results]
        
        # Calculate statistics
        def calc_stats(values):
            return {
                'mean': statistics.mean(values),
                'std': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values),
                'median': statistics.median(values)
            }
        
        success_stats = calc_stats(success_rates)
        response_stats = calc_stats(response_times)
        utilization_stats = calc_stats(utilizations)
        economic_stats = calc_stats(economic_efficiencies)
        
        # Display comprehensive results
        logger.info(f"🎯 SUCCESS RATE:")
        logger.info(f"   Mean: {success_stats['mean']:.1f}% ± {success_stats['std']:.1f}%")
        logger.info(f"   Range: {success_stats['min']:.1f}% - {success_stats['max']:.1f}%")
        
        logger.info(f"⏱️ RESPONSE TIME:")
        logger.info(f"   Mean: {response_stats['mean']:.2f}s ± {response_stats['std']:.2f}s")
        logger.info(f"   Range: {response_stats['min']:.2f}s - {response_stats['max']:.2f}s")
        
        logger.info(f"💾 PROVIDER UTILIZATION:")
        logger.info(f"   Mean: {utilization_stats['mean']:.2f} ± {utilization_stats['std']:.2f}")
        logger.info(f"   Range: {utilization_stats['min']:.2f} - {utilization_stats['max']:.2f}")
        
        logger.info(f"💰 ECONOMIC EFFICIENCY:")
        logger.info(f"   Mean: {economic_stats['mean']:.1f}% ± {economic_stats['std']:.1f}%")
        logger.info(f"   Range: {economic_stats['min']:.1f}% - {economic_stats['max']:.1f}%")
        
        logger.info(f"🔒 NETWORK CORRUPTIONS:")
        logger.info(f"   Total: {sum(corruptions)} across all iterations")
        logger.info(f"   Average per iteration: {statistics.mean(corruptions):.1f}")
        
        # Aggregate totals
        total_requests = sum(r['requests']['total'] for r in all_results)
        total_successful = sum(r['requests']['successful'] for r in all_results)
        total_earnings = sum(r['economics']['total_provider_earnings'] for r in all_results)
        
        logger.info(f"\n📈 AGGREGATE TOTALS:")
        logger.info(f"   Total Requests: {total_requests}")
        logger.info(f"   Total Successful: {total_successful}")
        logger.info(f"   Overall Success Rate: {(total_successful/max(total_requests,1))*100:.1f}%")
        logger.info(f"   Total Economic Value: ${total_earnings:.2f}")
        logger.info(f"   Simulation Time: {total_simulation_time:.1f}s")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"monte_carlo_results_{timestamp}.json"
        
        summary_data = {
            'simulation_config': {
                'iterations': iterations,
                'duration_per_iteration': duration_per_iteration,
                'num_buyers': num_buyers,
                'num_providers': num_providers,
                'total_simulation_time': total_simulation_time
            },
            'statistics': {
                'success_rate': success_stats,
                'response_time': response_stats,
                'utilization': utilization_stats,
                'economic_efficiency': economic_stats,
                'total_corruptions': sum(corruptions)
            },
            'raw_results': all_results
        }
        
        with open(results_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        logger.info(f"📄 Detailed results saved to {results_file}")
        
        # Generate summary report
        report_file = f"simulation_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write("DECENTRALIZED CLOUD STORAGE NETWORK SIMULATION REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Simulation Configuration:\n")
            f.write(f"  - Iterations: {iterations}\n")
            f.write(f"  - Duration per iteration: {duration_per_iteration}s\n")
            f.write(f"  - Buyers: {num_buyers}\n")
            f.write(f"  - Providers: {num_providers}\n")
            f.write(f"  - Total simulation time: {total_simulation_time:.1f}s\n\n")
            f.write(f"Key Performance Metrics:\n")
            f.write(f"  - Success Rate: {success_stats['mean']:.1f}% ± {success_stats['std']:.1f}%\n")
            f.write(f"  - Response Time: {response_stats['mean']:.2f}s ± {response_stats['std']:.2f}s\n")
            f.write(f"  - Provider Utilization: {utilization_stats['mean']:.2f} ± {utilization_stats['std']:.2f}\n")
            f.write(f"  - Economic Efficiency: {economic_stats['mean']:.1f}% ± {economic_stats['std']:.1f}%\n")
            f.write(f"  - Network Corruptions: {sum(corruptions)} total\n\n")
            f.write(f"System Robustness:\n")
            f.write(f"  - Total Requests Processed: {total_requests}\n")
            f.write(f"  - Overall Success Rate: {(total_successful/max(total_requests,1))*100:.1f}%\n")
            f.write(f"  - Total Economic Value Generated: ${total_earnings:.2f}\n")
        
        logger.info(f"📊 Summary report saved to {report_file}")
        
    else:
        logger.error("❌ No successful simulation iterations completed!")

if __name__ == "__main__":
    # Run the enhanced simulation
    asyncio.run(run_monte_carlo_simulation(
        iterations=3,           # Number of Monte Carlo iterations
        duration_per_iteration=30,  # Duration of each simulation run
        num_buyers=2,          # Number of buyer agents
        num_providers=3        # Number of storage provider agents
    ))
