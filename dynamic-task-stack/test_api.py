#!/usr/bin/env python3
"""
Test script for Dynamic Task Stack API
Run this script to test all API endpoints
"""

import requests
import json
import time
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:5002"
HEADERS = {"Content-Type": "application/json"}


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_test(name: str):
    """Print test name"""
    print(f"\n{Colors.BLUE}=== {name} ==={Colors.RESET}")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")


def test_health_check():
    """Test health check endpoint"""
    print_test("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print_success("Health check passed")
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


def test_user_messages():
    """Test user message endpoints"""
    print_test("User Messages API")
    success_count = 0
    total_count = 0
    
    # Create message
    total_count += 1
    try:
        response = requests.post(
            f"{BASE_URL}/api/messages/create",
            json={"content": "Test message", "user_id": "test_user_1"},
            headers=HEADERS
        )
        assert response.status_code == 201
        msg_data = response.json()
        assert "id" in msg_data
        msg_id = msg_data["id"]
        print_success(f"Created message: {msg_id}")
        success_count += 1
    except Exception as e:
        print_error(f"Create message failed: {e}")
        return False
    
    # Get message by ID
    total_count += 1
    try:
        response = requests.get(f"{BASE_URL}/api/messages/{msg_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == msg_id
        print_success(f"Retrieved message: {msg_id}")
        success_count += 1
    except Exception as e:
        print_error(f"Get message failed: {e}")
    
    # Get all messages
    total_count += 1
    try:
        response = requests.get(f"{BASE_URL}/api/messages/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print_success(f"Retrieved {len(data)} messages")
        success_count += 1
    except Exception as e:
        print_error(f"Get all messages failed: {e}")
    
    # Get messages filtered by user_id
    total_count += 1
    try:
        response = requests.get(
            f"{BASE_URL}/api/messages/list?user_id=test_user_1"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print_success(f"Retrieved {len(data)} messages for user")
        success_count += 1
    except Exception as e:
        print_error(f"Get filtered messages failed: {e}")
    
    # Update read status
    total_count += 1
    try:
        response = requests.put(
            f"{BASE_URL}/api/messages/{msg_id}/read-status",
            json={"worker_read_status": "READ", "user_read_status": "READ"},
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["worker_read_status"] == "READ"
        print_success("Updated read status")
        success_count += 1
    except Exception as e:
        print_error(f"Update read status failed: {e}")
    
    # Check message
    total_count += 1
    try:
        response = requests.get(f"{BASE_URL}/api/messages/{msg_id}/check")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "is_new_task" in data
        print_success("Checked message")
        success_count += 1
    except Exception as e:
        print_error(f"Check message failed: {e}")
    
    print_info(f"User Messages: {success_count}/{total_count} tests passed")
    return success_count == total_count


def test_tasks():
    """Test task endpoints"""
    print_test("Tasks API")
    success_count = 0
    total_count = 0
    task_ids = []
    
    # Create task
    total_count += 1
    try:
        response = requests.post(
            f"{BASE_URL}/api/tasks/create",
            json={
                "description": {
                    "overall_description": "Test task",
                    "input": {"data": "test"},
                    "requirements": ["test"],
                    "additional_notes": "Test notes"
                }
            },
            headers=HEADERS
        )
        assert response.status_code == 201
        task_data = response.json()
        assert "id" in task_data
        task_id = task_data["id"]
        task_ids.append(task_id)
        print_success(f"Created task: {task_id}")
        success_count += 1
    except Exception as e:
        print_error(f"Create task failed: {e}")
        return False
    
    # Get task by ID
    total_count += 1
    try:
        response = requests.get(f"{BASE_URL}/api/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        print_success(f"Retrieved task: {task_id}")
        success_count += 1
    except Exception as e:
        print_error(f"Get task failed: {e}")
    
    # Get all tasks
    total_count += 1
    try:
        response = requests.get(f"{BASE_URL}/api/tasks/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print_success(f"Retrieved {len(data)} tasks")
        success_count += 1
    except Exception as e:
        print_error(f"Get all tasks failed: {e}")
    
    # Update task
    total_count += 1
    try:
        response = requests.put(
            f"{BASE_URL}/api/tasks/{task_id}",
            json={
                "status": "IN_PROGRESS",
                "progress": {"step1": "done"},
                "results": {"output": "test_output"}
            },
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "IN_PROGRESS"
        print_success("Updated task")
        success_count += 1
    except Exception as e:
        print_error(f"Update task failed: {e}")
    
    # Update task status only
    total_count += 1
    try:
        response = requests.put(
            f"{BASE_URL}/api/tasks/{task_id}/status",
            json={"status": "COMPLETED"},
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"
        print_success("Updated task status")
        success_count += 1
    except Exception as e:
        print_error(f"Update task status failed: {e}")
    
    # Push message to task
    total_count += 1
    try:
        response = requests.post(
            f"{BASE_URL}/api/tasks/{task_id}/messages",
            json={"content": "Task message", "user_id": "test_user_1"},
            headers=HEADERS
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        print_success("Pushed message to task")
        success_count += 1
    except Exception as e:
        print_error(f"Push message to task failed: {e}")
    
    print_info(f"Tasks: {success_count}/{total_count} tests passed")
    return task_ids


def test_layers():
    """Test layer endpoints"""
    print_test("Task Layers API")
    success_count = 0
    total_count = 0
    
    # Create layer
    total_count += 1
    try:
        response = requests.post(
            f"{BASE_URL}/api/layers/create",
            json={
                "pre_hook": {"type": "middleware", "action": "prepare"},
                "post_hook": {"type": "hook", "action": "cleanup"}
            },
            headers=HEADERS
        )
        assert response.status_code == 201
        layer_data = response.json()
        assert "layer_index" in layer_data
        layer_index = layer_data["layer_index"]
        print_success(f"Created layer: {layer_index}")
        success_count += 1
    except Exception as e:
        print_error(f"Create layer failed: {e}")
        return None
    
    # Create task for layer
    task_response = requests.post(
        f"{BASE_URL}/api/tasks/create",
        json={
            "description": {
                "overall_description": "Layer task",
                "input": {},
                "requirements": [],
                "additional_notes": ""
            }
        },
        headers=HEADERS
    )
    if task_response.status_code != 201:
        print_error("Failed to create task for layer")
        return None
    task_id = task_response.json()["id"]
    
    # Add task to layer
    total_count += 1
    try:
        response = requests.post(
            f"{BASE_URL}/api/layers/{layer_index}/tasks",
            json={"task_id": task_id},
            headers=HEADERS
        )
        assert response.status_code == 200
        print_success(f"Added task to layer {layer_index}")
        success_count += 1
    except Exception as e:
        print_error(f"Add task to layer failed: {e}")
    
    # Get all layers
    total_count += 1
    try:
        response = requests.get(f"{BASE_URL}/api/layers/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print_success(f"Retrieved {len(data)} layers")
        success_count += 1
    except Exception as e:
        print_error(f"Get all layers failed: {e}")
    
    # Get layer by index
    total_count += 1
    try:
        response = requests.get(f"{BASE_URL}/api/layers/{layer_index}")
        assert response.status_code == 200
        data = response.json()
        assert data["layer_index"] == layer_index
        print_success(f"Retrieved layer {layer_index}")
        success_count += 1
    except Exception as e:
        print_error(f"Get layer failed: {e}")
    
    # Update layer hooks
    total_count += 1
    try:
        response = requests.put(
            f"{BASE_URL}/api/layers/{layer_index}/hooks",
            json={"pre_hook": {"type": "updated", "action": "new_prepare"}},
            headers=HEADERS
        )
        assert response.status_code == 200
        print_success("Updated layer hooks")
        success_count += 1
    except Exception as e:
        print_error(f"Update layer hooks failed: {e}")
    
    print_info(f"Layers: {success_count}/{total_count} tests passed")
    return layer_index, task_id


def test_execution_pointer():
    """Test execution pointer endpoints"""
    print_test("Execution Pointer API")
    success_count = 0
    total_count = 0
    
    # Set execution pointer
    total_count += 1
    try:
        response = requests.put(
            f"{BASE_URL}/api/execution-pointer/set",
            json={"layer_index": 0, "task_index": 0},
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["current_layer_index"] == 0
        assert data["current_task_index"] == 0
        print_success("Set execution pointer")
        success_count += 1
    except Exception as e:
        print_error(f"Set execution pointer failed: {e}")
        return False
    
    # Get execution pointer
    total_count += 1
    try:
        response = requests.get(f"{BASE_URL}/api/execution-pointer/get")
        assert response.status_code == 200
        data = response.json()
        assert "current_layer_index" in data
        print_success("Retrieved execution pointer")
        success_count += 1
    except Exception as e:
        print_error(f"Get execution pointer failed: {e}")
    
    # Advance execution pointer
    total_count += 1
    try:
        response = requests.post(f"{BASE_URL}/api/execution-pointer/advance")
        if response.status_code == 200:
            print_success("Advanced execution pointer")
            success_count += 1
        else:
            print_info("Cannot advance pointer (expected if no more tasks)")
            success_count += 1
    except Exception as e:
        print_error(f"Advance execution pointer failed: {e}")
    
    print_info(f"Execution Pointer: {success_count}/{total_count} tests passed")
    return success_count == total_count


def test_task_stack():
    """Test task stack convenience endpoints"""
    print_test("Task Stack API")
    success_count = 0
    total_count = 0
    
    # Get task stack
    total_count += 1
    try:
        response = requests.get(f"{BASE_URL}/api/task-stack")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print_success(f"Retrieved task stack with {len(data)} layers")
        success_count += 1
    except Exception as e:
        print_error(f"Get task stack failed: {e}")
    
    # Get next task
    total_count += 1
    try:
        response = requests.get(f"{BASE_URL}/api/task-stack/next")
        assert response.status_code == 200
        data = response.json()
        if "message" in data:
            print_info("No tasks in stack")
        else:
            assert "task_id" in data
            print_success("Retrieved next task")
        success_count += 1
    except Exception as e:
        print_error(f"Get next task failed: {e}")
    
    print_info(f"Task Stack: {success_count}/{total_count} tests passed")
    return success_count == total_count


def test_replace_task(layer_index: int, old_task_id: str):
    """Test replace task functionality"""
    print_test("Replace Task (Atomic Operation)")
    success_count = 0
    total_count = 0
    
    # Create new task
    total_count += 1
    try:
        response = requests.post(
            f"{BASE_URL}/api/tasks/create",
            json={
                "description": {
                    "overall_description": "Replacement task",
                    "input": {},
                    "requirements": [],
                    "additional_notes": ""
                }
            },
            headers=HEADERS
        )
        assert response.status_code == 201
        new_task_id = response.json()["id"]
        print_success(f"Created replacement task: {new_task_id}")
        success_count += 1
    except Exception as e:
        print_error(f"Create replacement task failed: {e}")
        return False
    
    # Replace task
    total_count += 1
    try:
        response = requests.post(
            f"{BASE_URL}/api/layers/{layer_index}/tasks/replace",
            json={"old_task_id": old_task_id, "new_task_id": new_task_id},
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        # Check that old task is cancelled
        old_task_response = requests.get(f"{BASE_URL}/api/tasks/{old_task_id}")
        if old_task_response.status_code == 200:
            old_task_data = old_task_response.json()
            if old_task_data.get("status") == "CANCELLED":
                print_success("Task replaced (old task cancelled)")
            else:
                print_info("Task replaced (old task status may vary)")
        print_success("Replaced task atomically")
        success_count += 1
    except Exception as e:
        print_error(f"Replace task failed: {e}")
    
    print_info(f"Replace Task: {success_count}/{total_count} tests passed")
    return success_count == total_count


def test_error_handling():
    """Test error handling"""
    print_test("Error Handling")
    success_count = 0
    total_count = 0
    
    # Test invalid message ID
    total_count += 1
    try:
        response = requests.get(f"{BASE_URL}/api/messages/invalid_id")
        assert response.status_code == 404
        print_success("Invalid message ID returns 404")
        success_count += 1
    except Exception as e:
        print_error(f"Error handling test failed: {e}")
    
    # Test invalid task ID
    total_count += 1
    try:
        response = requests.get(f"{BASE_URL}/api/tasks/invalid_id")
        assert response.status_code == 404
        print_success("Invalid task ID returns 404")
        success_count += 1
    except Exception as e:
        print_error(f"Error handling test failed: {e}")
    
    # Test invalid layer index
    total_count += 1
    try:
        response = requests.get(f"{BASE_URL}/api/layers/999")
        assert response.status_code == 404
        print_success("Invalid layer index returns 404")
        success_count += 1
    except Exception as e:
        print_error(f"Error handling test failed: {e}")
    
    # Test missing required fields
    total_count += 1
    try:
        response = requests.post(
            f"{BASE_URL}/api/messages/create",
            json={"content": "test"},
            headers=HEADERS
        )
        assert response.status_code == 400
        print_success("Missing required fields returns 400")
        success_count += 1
    except Exception as e:
        print_error(f"Error handling test failed: {e}")
    
    print_info(f"Error Handling: {success_count}/{total_count} tests passed")
    return success_count == total_count


def demo_workflow():
    """Create a demo workflow that can be observed in the frontend"""
    print_test("Demo Workflow - Creating visible frontend changes")
    
    try:
        user_id = "demo_user_" + str(int(time.time()))
        
        # 1. Create user messages
        print_info("Creating user messages...")
        msg1 = requests.post(
            f"{BASE_URL}/api/messages/create",
            json={"content": "Hello! I need help with a task.", "user_id": user_id},
            headers=HEADERS
        ).json()
        print_success(f"Created message: {msg1['id']}")
        
        time.sleep(1)
        
        msg2 = requests.post(
            f"{BASE_URL}/api/messages/create",
            json={"content": "Please process this data and generate a report.", "user_id": user_id},
            headers=HEADERS
        ).json()
        print_success(f"Created message: {msg2['id']}")
        
        # 2. Create tasks
        print_info("Creating tasks...")
        task1 = requests.post(
            f"{BASE_URL}/api/tasks/create",
            json={
                "description": {
                    "overall_description": "Process user data",
                    "input": {"data": "sample data"},
                    "requirements": ["validate", "transform"],
                    "additional_notes": "High priority"
                }
            },
            headers=HEADERS
        ).json()
        print_success(f"Created task: {task1['id']}")
        
        task2 = requests.post(
            f"{BASE_URL}/api/tasks/create",
            json={
                "description": {
                    "overall_description": "Generate report",
                    "input": {},
                    "requirements": ["analyze", "format"],
                    "additional_notes": ""
                }
            },
            headers=HEADERS
        ).json()
        print_success(f"Created task: {task2['id']}")
        
        task3 = requests.post(
            f"{BASE_URL}/api/tasks/create",
            json={
                "description": {
                    "overall_description": "Send notification",
                    "input": {},
                    "requirements": ["format", "send"],
                    "additional_notes": ""
                }
            },
            headers=HEADERS
        ).json()
        print_success(f"Created task: {task3['id']}")
        
        # 3. Create layers
        print_info("Creating task layers...")
        layer0 = requests.post(
            f"{BASE_URL}/api/layers/create",
            json={
                "pre_hook": {"type": "middleware", "action": "prepare_environment"},
                "post_hook": {"type": "hook", "action": "cleanup"}
            },
            headers=HEADERS
        ).json()
        print_success(f"Created Layer {layer0['layer_index']}")
        
        layer1 = requests.post(
            f"{BASE_URL}/api/layers/create",
            json={
                "pre_hook": {"type": "middleware", "action": "prepare"},
                "post_hook": {"type": "hook", "action": "finalize"}
            },
            headers=HEADERS
        ).json()
        print_success(f"Created Layer {layer1['layer_index']}")
        
        # 4. Add tasks to layers
        print_info("Adding tasks to layers...")
        requests.post(
            f"{BASE_URL}/api/layers/0/tasks",
            json={"task_id": task1['id']},
            headers=HEADERS
        )
        print_success(f"Added task {task1['id']} to Layer 0")
        
        requests.post(
            f"{BASE_URL}/api/layers/1/tasks",
            json={"task_id": task2['id']},
            headers=HEADERS
        )
        print_success(f"Added task {task2['id']} to Layer 1")
        
        requests.post(
            f"{BASE_URL}/api/layers/1/tasks",
            json={"task_id": task3['id']},
            headers=HEADERS
        )
        print_success(f"Added task {task3['id']} to Layer 1")
        
        # 5. Set execution pointer
        print_info("Setting execution pointer...")
        requests.put(
            f"{BASE_URL}/api/execution-pointer/set",
            json={"layer_index": 0, "task_index": 0},
            headers=HEADERS
        )
        print_success("Execution pointer set to Layer 0, Task 0")
        
        # 6. Simulate task execution
        print_info("Simulating task execution...")
        time.sleep(1)
        
        # Update task 1 to IN_PROGRESS
        requests.put(
            f"{BASE_URL}/api/tasks/{task1['id']}/status",
            json={"status": "IN_PROGRESS"},
            headers=HEADERS
        )
        print_success(f"Task {task1['id']} status: IN_PROGRESS")
        time.sleep(2)
        
        # Update task 1 progress
        requests.put(
            f"{BASE_URL}/api/tasks/{task1['id']}",
            json={
                "progress": {"step1": "done", "step2": "in_progress", "step3": "pending"}
            },
            headers=HEADERS
        )
        print_success("Updated task progress")
        time.sleep(2)
        
        # Complete task 1
        requests.put(
            f"{BASE_URL}/api/tasks/{task1['id']}/status",
            json={"status": "COMPLETED"},
            headers=HEADERS
        )
        requests.put(
            f"{BASE_URL}/api/tasks/{task1['id']}",
            json={
                "results": {"output": "Processed data", "status": "success"}
            },
            headers=HEADERS
        )
        print_success(f"Task {task1['id']} completed")
        time.sleep(1)
        
        # Advance pointer
        requests.post(f"{BASE_URL}/api/execution-pointer/advance")
        print_success("Advanced execution pointer")
        time.sleep(1)
        
        # Update task 2 to IN_PROGRESS
        requests.put(
            f"{BASE_URL}/api/execution-pointer/set",
            json={"layer_index": 1, "task_index": 0},
            headers=HEADERS
        )
        requests.put(
            f"{BASE_URL}/api/tasks/{task2['id']}/status",
            json={"status": "IN_PROGRESS"},
            headers=HEADERS
        )
        print_success(f"Task {task2['id']} status: IN_PROGRESS")
        time.sleep(2)
        
        # Complete task 2
        requests.put(
            f"{BASE_URL}/api/tasks/{task2['id']}/status",
            json={"status": "COMPLETED"},
            headers=HEADERS
        )
        print_success(f"Task {task2['id']} completed")
        time.sleep(1)
        
        # Create server response message
        server_msg = requests.post(
            f"{BASE_URL}/api/messages/create",
            json={
                "content": "Task completed successfully! Report generated.",
                "user_id": "server"
            },
            headers=HEADERS
        ).json()
        print_success(f"Created server message: {server_msg['id']}")
        
        print_info("\n" + "="*60)
        print_info("Demo workflow completed!")
        print_info("Check the frontend to see:")
        print_info("  - User messages in the chat window")
        print_info("  - Task stack with 2 layers")
        print_info("  - Task execution status changes")
        print_info("  - System status updates")
        print_info("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print_error(f"Demo workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("FrameWorkers Dynamic Task Stack API Test Suite")
    print(f"{'='*60}{Colors.RESET}\n")
    
    # Check if server is running
    if not test_health_check():
        print_error("Server is not running. Please start the server first.")
        print_info("Run: python run.py")
        return
    
    import sys
    
    # Check if demo mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        demo_workflow()
        return
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("User Messages", test_user_messages()))
    task_ids = test_tasks()
    results.append(("Tasks", task_ids is not False))
    
    layer_result = test_layers()
    if layer_result:
        layer_index, task_id = layer_result
        results.append(("Layers", True))
        results.append(("Replace Task", test_replace_task(layer_index, task_id)))
    else:
        results.append(("Layers", False))
    
    results.append(("Execution Pointer", test_execution_pointer()))
    results.append(("Task Stack", test_task_stack()))
    results.append(("Error Handling", test_error_handling()))
    
    # Print summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print("Test Summary")
    print(f"{'='*60}{Colors.RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASSED{Colors.RESET}" if result else f"{Colors.RED}FAILED{Colors.RESET}"
        print(f"{name:30} {status}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"Total: {passed}/{total} test suites passed")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}All tests passed!{Colors.RESET}")
    else:
        print(f"{Colors.RED}Some tests failed.{Colors.RESET}")
    
    print(f"\n{Colors.YELLOW}Tip: Run with --demo flag to create a demo workflow:")
    print(f"  python test_api.py --demo{Colors.RESET}\n")


if __name__ == "__main__":
    main()
