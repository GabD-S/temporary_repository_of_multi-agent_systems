"""
Quick balanced test of the enhanced cloud storage simulation
"""

import asyncio
import logging
import sys
import os

# Add the current directory to the path so we can import the simulation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now import our simulation modules
from enhanced_cloud_storage import (
    run_single_simulation, global_metrics, BuyerAgent, 
    StorageProviderAgent, IntermediaryNetworkAgent, MessageBus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("QuickTest")

async def balanced_test():
    """Run a balanced test with matching price ranges"""
    logger.info("🧪 Running balanced test simulation...")
    
    # Reset global metrics
    global_metrics.reset()
    
    # Create message bus
    message_bus = MessageBus()
    
    # Create network agent
    network = IntermediaryNetworkAgent("network", message_bus, corruption_probability=0.02)
    await network.start()
    
    # Create provider agents with reasonable prices
    providers = []
    for i in range(2):
        provider = StorageProviderAgent(
            agent_id=f"provider{i}",
            broker_id="network",
            message_bus=message_bus,
            total_space_gb=150,  # Smaller for testing
            base_price_per_gb_hour=0.4,  # Lower base price
            failure_probability=0.05  # Lower failure rate for testing
        )
        providers.append(provider)
        await provider.start()
        await asyncio.sleep(0.5)
    
    # Create buyer agents with matching budgets
    buyers = []
    for i in range(2):
        buyer = BuyerAgent(
            agent_id=f"buyer{i}",
            broker_id="network",
            message_bus=message_bus,
            request_interval=(3.0, 6.0),
            budget_per_hour=25.0  # Higher budget to match provider prices
        )
        buyers.append(buyer)
        await buyer.start()
        await asyncio.sleep(0.5)
    
    # Let simulation run for 15 seconds
    logger.info("⏱️ Running simulation for 15 seconds...")
    await asyncio.sleep(15)
    
    # Stop all agents
    for agent in [network] + providers + buyers:
        await agent.stop()
    
    # Wait for final processing
    await asyncio.sleep(1)
    
    # Get metrics
    metrics = global_metrics.get_summary()
    
    # Display results
    logger.info("📊 SIMULATION RESULTS:")
    logger.info(f"   Requests: {metrics['requests']['total']}")
    logger.info(f"   Success Rate: {metrics['requests']['success_rate']:.1f}%")
    logger.info(f"   Avg Response Time: {metrics['requests']['avg_response_time']:.2f}s")
    logger.info(f"   Contracts Created: {metrics['contracts']['created']}")
    logger.info(f"   Provider Utilization: {metrics['providers']['avg_utilization']:.2f}")
    logger.info(f"   Total Earnings: ${metrics['providers']['total_earnings']:.2f}")
    logger.info(f"   Network Corruptions: {metrics['network']['corruptions']}")
    
    # Show agent stats
    logger.info("🏢 Network Stats:")
    for key, value in network.stats.items():
        logger.info(f"   {key}: {value}")
    
    logger.info("💾 Provider Stats:")
    for i, provider in enumerate(providers):
        logger.info(f"   Provider {i}: {provider.stats}")
    
    logger.info("🛒 Buyer Stats:")
    for i, buyer in enumerate(buyers):
        logger.info(f"   Buyer {i}: {buyer.stats}")
    
    logger.info("✅ Balanced test completed successfully!")
    
    return metrics

if __name__ == "__main__":
    result = asyncio.run(balanced_test())
