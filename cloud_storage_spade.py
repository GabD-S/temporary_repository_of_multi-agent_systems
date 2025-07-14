"""
Decentralized Cloud Storage Network Simulation using SPADE
Enhanced version with real storage capacity, contract duration, network latency,
and reputation system with Monte Carlo metrics.
"""

import asyncio
import random
import time
import json
import logging
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, PeriodicBehaviour
from spade.message import Message
from spade.template import Template

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CloudStorageSpade")

@dataclass
class StorageRequest:
    """Storage request data structure"""
    buyer_id: str
    space_gb: int
    duration_hours: float
    max_price: float
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
    price: float
    start_time: float
    end_time: float
    status: str  # 'active', 'completed', 'failed'

@dataclass
class ProviderInfo:
    """Provider information for the network"""
    agent_id: str
    total_space_gb: int
    available_space_gb: int
    reputation: float
    price_per_gb_hour: float
    last_seen: float
    success_count: int
    failure_count: int

class SimulationMetrics:
    """Collects and manages simulation metrics"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.requests_sent = 0
        self.requests_successful = 0
        self.requests_failed = 0
        self.response_times = []
        self.contract_durations = []
        self.provider_utilizations = []
        self.network_corruptions = 0
        self.provider_failures = 0
        self.start_time = time.time()
        
    def add_response_time(self, response_time: float):
        self.response_times.append(response_time)
    
    def add_successful_request(self):
        self.requests_successful += 1
    
    def add_failed_request(self):
        self.requests_failed += 1
    
    def add_sent_request(self):
        self.requests_sent += 1
    
    def add_contract_duration(self, duration: float):
        self.contract_durations.append(duration)
    
    def add_provider_utilization(self, utilization: float):
        self.provider_utilizations.append(utilization)
    
    def add_network_corruption(self):
        self.network_corruptions += 1
    
    def add_provider_failure(self):
        self.provider_failures += 1
    
    def get_summary(self) -> Dict:
        """Returns summary of collected metrics"""
        total_time = time.time() - self.start_time
        
        return {
            'total_requests': self.requests_sent,
            'successful_requests': self.requests_successful,
            'failed_requests': self.requests_failed,
            'success_rate': (self.requests_successful / max(self.requests_sent, 1)) * 100,
            'failure_rate': (self.requests_failed / max(self.requests_sent, 1)) * 100,
            'avg_response_time': statistics.mean(self.response_times) if self.response_times else 0,
            'std_response_time': statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0,
            'avg_contract_duration': statistics.mean(self.contract_durations) if self.contract_durations else 0,
            'avg_provider_utilization': statistics.mean(self.provider_utilizations) if self.provider_utilizations else 0,
            'network_corruptions': self.network_corruptions,
            'provider_failures': self.provider_failures,
            'simulation_duration': total_time
        }

# Global metrics instance
global_metrics = SimulationMetrics()

class NetworkLatencyBehaviour:
    """Mixin to add network latency simulation"""
    
    @staticmethod
    async def simulate_network_delay(min_delay: float = 0.1, max_delay: float = 0.8):
        """Simulates network latency"""
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)

class BuyerAgent(Agent):
    """
    Buyer agent that periodically requests storage space
    """
    
    def __init__(self, jid: str, password: str, network_jid: str, 
                 request_interval: Tuple[int, int] = (5, 15)):
        super().__init__(jid, password)
        self.network_jid = network_jid
        self.request_interval = request_interval
        self.pending_requests = {}
        self.completed_contracts = []
        self.stats = {
            'requests_sent': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'total_spent': 0.0
        }
    
    async def setup(self):
        logger.info(f"🛒 Buyer {self.jid} starting up")
        
        # Add request behavior
        request_behaviour = self.RequestStorageBehaviour()
        self.add_behaviour(request_behaviour)
        
        # Add response handler
        response_template = Template()
        response_template.set_metadata("performative", "storage-response")
        response_behaviour = self.HandleResponseBehaviour()
        self.add_behaviour(response_behaviour, response_template)
    
    class RequestStorageBehaviour(PeriodicBehaviour, NetworkLatencyBehaviour):
        """Periodically sends storage requests"""
        
        async def run(self):
            # Generate storage request
            space_needed = random.randint(1, 20)  # 1-20 GB
            duration = random.uniform(0.5, 4.0)   # 0.5-4 hours
            max_price = random.uniform(0.1, 1.0)  # $0.1-1.0 per GB/hour
            request_id = f"REQ-{int(time.time())}-{random.randint(1000, 9999)}"
            
            request = StorageRequest(
                buyer_id=str(self.agent.jid),
                space_gb=space_needed,
                duration_hours=duration,
                max_price=max_price,
                timestamp=time.time(),
                request_id=request_id
            )
            
            # Store pending request
            self.agent.pending_requests[request_id] = request
            
            # Create message
            msg = Message(to=self.agent.network_jid)
            msg.set_metadata("performative", "storage-request")
            msg.body = json.dumps(asdict(request))
            
            # Simulate network latency
            await self.simulate_network_delay()
            
            # Send message
            await self.send(msg)
            
            self.agent.stats['requests_sent'] += 1
            global_metrics.add_sent_request()
            
            logger.info(f"🛒 Buyer {self.agent.jid} requested {space_needed}GB for {duration:.1f}h at max ${max_price:.2f}/GB/h")
        
        async def on_start(self):
            # Random interval between requests
            interval = random.randint(*self.agent.request_interval)
            self.period = interval
    
    class HandleResponseBehaviour(CyclicBehaviour):
        """Handles responses from the network"""
        
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    response_data = json.loads(msg.body)
                    request_id = response_data.get('request_id')
                    
                    if request_id in self.agent.pending_requests:
                        original_request = self.agent.pending_requests[request_id]
                        response_time = time.time() - original_request.timestamp
                        
                        global_metrics.add_response_time(response_time)
                        
                        if response_data.get('status') == 'success':
                            self.agent.stats['requests_successful'] += 1
                            self.agent.stats['total_spent'] += response_data.get('total_cost', 0)
                            global_metrics.add_successful_request()
                            
                            # Store contract info
                            contract = StorageContract(**response_data['contract'])
                            self.agent.completed_contracts.append(contract)
                            global_metrics.add_contract_duration(contract.duration_hours)
                            
                            logger.info(f"✅ Buyer {self.agent.jid} request {request_id} accepted - Cost: ${response_data.get('total_cost', 0):.2f}")
                        else:
                            self.agent.stats['requests_failed'] += 1
                            global_metrics.add_failed_request()
                            logger.info(f"❌ Buyer {self.agent.jid} request {request_id} rejected: {response_data.get('reason', 'unknown')}")
                        
                        # Remove from pending
                        del self.agent.pending_requests[request_id]
                
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in response: {msg.body}")

class StorageProviderAgent(Agent):
    """
    Storage provider agent with finite capacity and reputation management
    """
    
    def __init__(self, jid: str, password: str, network_jid: str, 
                 total_space_gb: int, price_per_gb_hour: float = 0.5, 
                 failure_probability: float = 0.1):
        super().__init__(jid, password)
        self.network_jid = network_jid
        self.total_space_gb = total_space_gb
        self.available_space_gb = total_space_gb
        self.price_per_gb_hour = price_per_gb_hour
        self.failure_probability = failure_probability
        self.active_contracts = {}
        self.completed_contracts = []
        self.reputation = 5.0  # Initial reputation
        self.stats = {
            'requests_received': 0,
            'requests_accepted': 0,
            'requests_rejected': 0,
            'total_earnings': 0.0,
            'uptime': 0.0
        }
        self.start_time = time.time()
    
    async def setup(self):
        logger.info(f"💾 Provider {self.jid} starting with {self.total_space_gb}GB at ${self.price_per_gb_hour:.2f}/GB/h")
        
        # Register with network
        await self.register_with_network()
        
        # Add allocation request handler
        allocation_template = Template()
        allocation_template.set_metadata("performative", "allocation-request")
        allocation_behaviour = self.HandleAllocationBehaviour()
        self.add_behaviour(allocation_behaviour, allocation_template)
        
        # Add periodic status update
        status_behaviour = self.StatusUpdateBehaviour()
        self.add_behaviour(status_behaviour)
        
        # Add contract management
        contract_behaviour = self.ContractManagementBehaviour()
        self.add_behaviour(contract_behaviour)
    
    async def register_with_network(self):
        """Register provider with the network"""
        provider_info = ProviderInfo(
            agent_id=str(self.jid),
            total_space_gb=self.total_space_gb,
            available_space_gb=self.available_space_gb,
            reputation=self.reputation,
            price_per_gb_hour=self.price_per_gb_hour,
            last_seen=time.time(),
            success_count=0,
            failure_count=0
        )
        
        msg = Message(to=self.network_jid)
        msg.set_metadata("performative", "provider-registration")
        msg.body = json.dumps(asdict(provider_info))
        
        await self.send(msg)
        logger.info(f"📋 Provider {self.jid} registered with network")
    
    class HandleAllocationBehaviour(CyclicBehaviour, NetworkLatencyBehaviour):
        """Handles allocation requests from the network"""
        
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    request_data = json.loads(msg.body)
                    contract_data = request_data['contract']
                    
                    self.agent.stats['requests_received'] += 1
                    
                    # Simulate provider decision-making delay
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    
                    # Check if we can fulfill the request
                    space_needed = contract_data['space_gb']
                    can_allocate = (
                        self.agent.available_space_gb >= space_needed and
                        random.random() > self.agent.failure_probability  # Simulate random failures
                    )
                    
                    response = {
                        'contract_id': contract_data['contract_id'],
                        'provider_id': str(self.agent.jid),
                        'request_id': request_data['request_id']
                    }
                    
                    if can_allocate:
                        # Accept the contract
                        contract = StorageContract(**contract_data)
                        self.agent.active_contracts[contract.contract_id] = contract
                        self.agent.available_space_gb -= space_needed
                        self.agent.stats['requests_accepted'] += 1
                        self.agent.stats['total_earnings'] += contract.price
                        
                        response['status'] = 'accepted'
                        response['estimated_completion'] = contract.end_time
                        
                        logger.info(f"🟢 Provider {self.agent.jid} accepted contract {contract.contract_id} ({space_needed}GB)")
                    else:
                        # Reject the contract
                        self.agent.stats['requests_rejected'] += 1
                        response['status'] = 'rejected'
                        response['reason'] = 'insufficient_space' if self.agent.available_space_gb < space_needed else 'provider_failure'
                        
                        global_metrics.add_provider_failure()
                        logger.info(f"🔴 Provider {self.agent.jid} rejected contract {contract_data['contract_id']}")
                    
                    # Send response back to network
                    reply = Message(to=str(msg.sender))
                    reply.set_metadata("performative", "allocation-response")
                    reply.body = json.dumps(response)
                    
                    # Simulate network latency
                    await self.simulate_network_delay()
                    await self.send(reply)
                    
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in allocation request: {msg.body}")
    
    class StatusUpdateBehaviour(PeriodicBehaviour):
        """Periodically updates status with the network"""
        
        async def run(self):
            # Update utilization metrics
            utilization = (self.agent.total_space_gb - self.agent.available_space_gb) / self.agent.total_space_gb
            global_metrics.add_provider_utilization(utilization)
            
            # Update uptime
            self.agent.stats['uptime'] = time.time() - self.agent.start_time
            
            # Send status update to network
            status_update = {
                'provider_id': str(self.agent.jid),
                'available_space_gb': self.agent.available_space_gb,
                'active_contracts': len(self.agent.active_contracts),
                'reputation': self.agent.reputation,
                'utilization': utilization
            }
            
            msg = Message(to=self.agent.network_jid)
            msg.set_metadata("performative", "status-update")
            msg.body = json.dumps(status_update)
            
            await self.send(msg)
        
        async def on_start(self):
            self.period = 10  # Update every 10 seconds
    
    class ContractManagementBehaviour(PeriodicBehaviour):
        """Manages active contracts and releases space when contracts expire"""
        
        async def run(self):
            current_time = time.time()
            completed_contracts = []
            
            for contract_id, contract in self.agent.active_contracts.items():
                if current_time >= contract.end_time:
                    # Contract completed
                    self.agent.available_space_gb += contract.space_gb
                    contract.status = 'completed'
                    self.agent.completed_contracts.append(contract)
                    completed_contracts.append(contract_id)
                    
                    logger.info(f"📦 Provider {self.agent.jid} completed contract {contract_id} - Released {contract.space_gb}GB")
            
            # Remove completed contracts
            for contract_id in completed_contracts:
                del self.agent.active_contracts[contract_id]
        
        async def on_start(self):
            self.period = 5  # Check every 5 seconds

class IntermediaryNetworkAgent(Agent):
    """
    Central network agent that mediates between buyers and providers
    Implements reputation system and handles contract negotiations
    """
    
    def __init__(self, jid: str, password: str, corruption_probability: float = 0.05):
        super().__init__(jid, password)
        self.providers = {}  # provider_id -> ProviderInfo
        self.pending_requests = {}  # request_id -> (buyer_jid, request_data)
        self.active_contracts = {}  # contract_id -> StorageContract
        self.corruption_probability = corruption_probability
        self.stats = {
            'requests_processed': 0,
            'successful_allocations': 0,
            'failed_allocations': 0,
            'provider_count': 0,
            'corrupted_contracts': 0
        }
    
    async def setup(self):
        logger.info(f"🏢 Network {self.jid} starting up")
        
        # Handle provider registrations
        registration_template = Template()
        registration_template.set_metadata("performative", "provider-registration")
        registration_behaviour = self.HandleRegistrationBehaviour()
        self.add_behaviour(registration_behaviour, registration_template)
        
        # Handle storage requests
        request_template = Template()
        request_template.set_metadata("performative", "storage-request")
        request_behaviour = self.HandleStorageRequestBehaviour()
        self.add_behaviour(request_behaviour, request_template)
        
        # Handle allocation responses
        allocation_template = Template()
        allocation_template.set_metadata("performative", "allocation-response")
        allocation_behaviour = self.HandleAllocationResponseBehaviour()
        self.add_behaviour(allocation_behaviour, allocation_template)
        
        # Handle status updates
        status_template = Template()
        status_template.set_metadata("performative", "status-update")
        status_behaviour = self.HandleStatusUpdateBehaviour()
        self.add_behaviour(status_behaviour, status_template)
        
        # Periodic provider cleanup
        cleanup_behaviour = self.ProviderCleanupBehaviour()
        self.add_behaviour(cleanup_behaviour)
    
    class HandleRegistrationBehaviour(CyclicBehaviour):
        """Handles provider registration requests"""
        
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    provider_info = ProviderInfo(**json.loads(msg.body))
                    self.agent.providers[provider_info.agent_id] = provider_info
                    self.agent.stats['provider_count'] = len(self.agent.providers)
                    
                    logger.info(f"📋 Network registered provider {provider_info.agent_id} with {provider_info.total_space_gb}GB")
                    
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in registration: {msg.body}")
    
    class HandleStorageRequestBehaviour(CyclicBehaviour, NetworkLatencyBehaviour):
        """Handles storage requests from buyers"""
        
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    request_data = json.loads(msg.body)
                    request = StorageRequest(**request_data)
                    
                    self.agent.stats['requests_processed'] += 1
                    self.agent.pending_requests[request.request_id] = (str(msg.sender), request)
                    
                    logger.info(f"🏢 Network received request {request.request_id} from {request.buyer_id}")
                    
                    # Find suitable provider
                    selected_provider = self.select_provider(request)
                    
                    if selected_provider:
                        # Create contract
                        contract_id = f"CONT-{int(time.time())}-{random.randint(1000, 9999)}"
                        total_cost = request.space_gb * request.duration_hours * selected_provider.price_per_gb_hour
                        
                        contract = StorageContract(
                            contract_id=contract_id,
                            buyer_id=request.buyer_id,
                            provider_id=selected_provider.agent_id,
                            space_gb=request.space_gb,
                            duration_hours=request.duration_hours,
                            price=total_cost,
                            start_time=time.time(),
                            end_time=time.time() + (request.duration_hours * 3600),
                            status='pending'
                        )
                        
                        # Send allocation request to provider
                        allocation_msg = Message(to=selected_provider.agent_id)
                        allocation_msg.set_metadata("performative", "allocation-request")
                        allocation_msg.body = json.dumps({
                            'request_id': request.request_id,
                            'contract': asdict(contract)
                        })
                        
                        # Simulate network latency
                        await self.simulate_network_delay()
                        await self.send(allocation_msg)
                        
                        logger.info(f"🏢 Network forwarded request {request.request_id} to provider {selected_provider.agent_id}")
                    else:
                        # No suitable provider found
                        await self.send_failure_response(str(msg.sender), request.request_id, "no_suitable_provider")
                        self.agent.stats['failed_allocations'] += 1
                
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in storage request: {msg.body}")
        
        def select_provider(self, request: StorageRequest) -> Optional[ProviderInfo]:
            """Select best provider based on reputation, capacity, and price"""
            suitable_providers = []
            
            for provider in self.agent.providers.values():
                # Check if provider meets requirements
                if (provider.available_space_gb >= request.space_gb and
                    provider.price_per_gb_hour <= request.max_price and
                    provider.reputation >= 2.0 and  # Minimum reputation threshold
                    time.time() - provider.last_seen < 60):  # Provider is active
                    suitable_providers.append(provider)
            
            if not suitable_providers:
                return None
            
            # Select provider based on weighted reputation and price
            def provider_score(p: ProviderInfo) -> float:
                # Higher reputation and lower price = higher score
                reputation_score = p.reputation / 10.0  # Normalize to 0-1
                price_score = 1.0 - (p.price_per_gb_hour / request.max_price)  # Normalize to 0-1
                return (reputation_score * 0.7) + (price_score * 0.3)  # Weight reputation more
            
            suitable_providers.sort(key=provider_score, reverse=True)
            return suitable_providers[0]
        
        async def send_failure_response(self, buyer_jid: str, request_id: str, reason: str):
            """Send failure response to buyer"""
            response = {
                'request_id': request_id,
                'status': 'failure',
                'reason': reason
            }
            
            msg = Message(to=buyer_jid)
            msg.set_metadata("performative", "storage-response")
            msg.body = json.dumps(response)
            
            await self.send(msg)
            logger.info(f"🏢 Network sent failure response for request {request_id}: {reason}")
    
    class HandleAllocationResponseBehaviour(CyclicBehaviour, NetworkLatencyBehaviour):
        """Handles responses from providers"""
        
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    response_data = json.loads(msg.body)
                    request_id = response_data['request_id']
                    contract_id = response_data['contract_id']
                    provider_id = response_data['provider_id']
                    
                    if request_id in self.agent.pending_requests:
                        buyer_jid, original_request = self.agent.pending_requests[request_id]
                        
                        # Update provider reputation
                        if provider_id in self.agent.providers:
                            provider = self.agent.providers[provider_id]
                            if response_data['status'] == 'accepted':
                                provider.success_count += 1
                                provider.reputation = min(provider.reputation * 1.05, 10.0)
                            else:
                                provider.failure_count += 1
                                provider.reputation = max(provider.reputation * 0.95, 0.5)
                        
                        # Prepare response to buyer
                        if response_data['status'] == 'accepted':
                            self.agent.stats['successful_allocations'] += 1
                            
                            # Simulate potential contract corruption
                            corrupted = random.random() < self.agent.corruption_probability
                            if corrupted:
                                self.agent.stats['corrupted_contracts'] += 1
                                global_metrics.add_network_corruption()
                                response_status = 'failure'
                                response_reason = 'network_corruption'
                                logger.warning(f"⚠️ Network corrupted contract {contract_id}!")
                            else:
                                response_status = 'success'
                                response_reason = None
                            
                            buyer_response = {
                                'request_id': request_id,
                                'status': response_status,
                                'contract': {
                                    'contract_id': contract_id,
                                    'buyer_id': original_request.buyer_id,
                                    'provider_id': provider_id,
                                    'space_gb': original_request.space_gb,
                                    'duration_hours': original_request.duration_hours,
                                    'price': original_request.space_gb * original_request.duration_hours * self.agent.providers[provider_id].price_per_gb_hour,
                                    'start_time': time.time(),
                                    'end_time': time.time() + (original_request.duration_hours * 3600),
                                    'status': 'active'
                                },
                                'total_cost': original_request.space_gb * original_request.duration_hours * self.agent.providers[provider_id].price_per_gb_hour
                            }
                            
                            if corrupted:
                                buyer_response['reason'] = response_reason
                        else:
                            self.agent.stats['failed_allocations'] += 1
                            buyer_response = {
                                'request_id': request_id,
                                'status': 'failure',
                                'reason': response_data.get('reason', 'provider_rejected')
                            }
                        
                        # Send response to buyer
                        buyer_msg = Message(to=buyer_jid)
                        buyer_msg.set_metadata("performative", "storage-response")
                        buyer_msg.body = json.dumps(buyer_response)
                        
                        # Simulate network latency
                        await self.simulate_network_delay()
                        await self.send(buyer_msg)
                        
                        # Remove from pending
                        del self.agent.pending_requests[request_id]
                
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in allocation response: {msg.body}")
    
    class HandleStatusUpdateBehaviour(CyclicBehaviour):
        """Handles status updates from providers"""
        
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    status_data = json.loads(msg.body)
                    provider_id = status_data['provider_id']
                    
                    if provider_id in self.agent.providers:
                        provider = self.agent.providers[provider_id]
                        provider.available_space_gb = status_data['available_space_gb']
                        provider.reputation = status_data['reputation']
                        provider.last_seen = time.time()
                
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in status update: {msg.body}")
    
    class ProviderCleanupBehaviour(PeriodicBehaviour):
        """Removes inactive providers"""
        
        async def run(self):
            current_time = time.time()
            inactive_providers = []
            
            for provider_id, provider in self.agent.providers.items():
                if current_time - provider.last_seen > 120:  # 2 minutes timeout
                    inactive_providers.append(provider_id)
            
            for provider_id in inactive_providers:
                del self.agent.providers[provider_id]
                logger.info(f"🧹 Network removed inactive provider {provider_id}")
            
            self.agent.stats['provider_count'] = len(self.agent.providers)
        
        async def on_start(self):
            self.period = 30  # Cleanup every 30 seconds

async def run_single_simulation(duration: int = 60) -> Dict:
    """Run a single simulation iteration"""
    logger.info(f"🚀 Starting simulation for {duration} seconds")
    
    # Reset metrics
    global_metrics.reset()
    
    # Create network agent
    network_agent = IntermediaryNetworkAgent("network@localhost", "network_pass")
    await network_agent.start()
    
    # Create provider agents
    providers = []
    for i in range(3):
        provider_jid = f"provider{i}@localhost"
        provider = StorageProviderAgent(
            jid=provider_jid,
            password=f"provider{i}_pass",
            network_jid="network@localhost",
            total_space_gb=random.randint(50, 150),
            price_per_gb_hour=random.uniform(0.3, 0.8),
            failure_probability=random.uniform(0.05, 0.15)
        )
        providers.append(provider)
        await provider.start()
        await asyncio.sleep(1)  # Give time for registration
    
    # Create buyer agents
    buyers = []
    for i in range(2):
        buyer_jid = f"buyer{i}@localhost"
        buyer = BuyerAgent(
            jid=buyer_jid,
            password=f"buyer{i}_pass",
            network_jid="network@localhost",
            request_interval=(5, 15)
        )
        buyers.append(buyer)
        await buyer.start()
        await asyncio.sleep(0.5)
    
    # Let simulation run
    await asyncio.sleep(duration)
    
    # Stop all agents
    for agent in [network_agent] + providers + buyers:
        await agent.stop()
    
    # Collect metrics
    metrics = global_metrics.get_summary()
    
    # Add agent-specific stats
    metrics['network_stats'] = network_agent.stats
    metrics['provider_stats'] = [p.stats for p in providers]
    metrics['buyer_stats'] = [b.stats for b in buyers]
    
    return metrics

async def run_monte_carlo_simulation(iterations: int = 5, duration_per_iteration: int = 45):
    """Run Monte Carlo simulation with multiple iterations"""
    logger.info(f"🎯 Starting Monte Carlo simulation: {iterations} iterations of {duration_per_iteration}s each")
    
    all_results = []
    
    for i in range(iterations):
        logger.info(f"\n=== ITERATION {i+1}/{iterations} ===")
        
        try:
            # Run single simulation
            result = await run_single_simulation(duration_per_iteration)
            all_results.append(result)
            
            # Log iteration results
            logger.info(f"📊 Iteration {i+1} Results:")
            logger.info(f"  Success Rate: {result['success_rate']:.2f}%")
            logger.info(f"  Avg Response Time: {result['avg_response_time']:.2f}s")
            logger.info(f"  Provider Utilization: {result['avg_provider_utilization']:.2f}")
            logger.info(f"  Network Corruptions: {result['network_corruptions']}")
            
        except Exception as e:
            logger.error(f"Error in iteration {i+1}: {e}")
            continue
        
        # Small break between iterations
        if i < iterations - 1:
            await asyncio.sleep(3)
    
    # Calculate aggregate statistics
    if all_results:
        logger.info("\n🔥 MONTE CARLO SIMULATION RESULTS 🔥")
        logger.info("=" * 50)
        
        # Calculate means and standard deviations
        success_rates = [r['success_rate'] for r in all_results]
        response_times = [r['avg_response_time'] for r in all_results]
        utilizations = [r['avg_provider_utilization'] for r in all_results]
        corruptions = [r['network_corruptions'] for r in all_results]
        
        logger.info(f"Success Rate: {statistics.mean(success_rates):.2f}% ± {statistics.stdev(success_rates) if len(success_rates) > 1 else 0:.2f}%")
        logger.info(f"Response Time: {statistics.mean(response_times):.2f}s ± {statistics.stdev(response_times) if len(response_times) > 1 else 0:.2f}s")
        logger.info(f"Provider Utilization: {statistics.mean(utilizations):.2f} ± {statistics.stdev(utilizations) if len(utilizations) > 1 else 0:.2f}")
        logger.info(f"Network Corruptions: {statistics.mean(corruptions):.1f} ± {statistics.stdev(corruptions) if len(corruptions) > 1 else 0:.1f}")
        
        # Additional statistics
        total_requests = sum(r['total_requests'] for r in all_results)
        total_successful = sum(r['successful_requests'] for r in all_results)
        
        logger.info(f"\nAggregate Statistics:")
        logger.info(f"Total Requests: {total_requests}")
        logger.info(f"Total Successful: {total_successful}")
        logger.info(f"Overall Success Rate: {(total_successful/max(total_requests,1))*100:.2f}%")
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"simulation_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        logger.info(f"📄 Results saved to {results_file}")
        
    else:
        logger.error("No successful simulation iterations!")

if __name__ == "__main__":
    # Run the simulation
    asyncio.run(run_monte_carlo_simulation(iterations=3, duration_per_iteration=30))
