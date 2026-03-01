# ADCP MCP Integration Test Prompts

## Server Information

**Server Name**: adcp-tools
**Description**: MCP server for ADCP cyclic peptide conformational sampling
**Type**: Submit-based API (all operations are async due to long runtime)

## Tool Discovery Tests

### Prompt 1: List All Tools
"What MCP tools are available from the adcp-tools server? Give me a brief description of each tool and what it does."

**Expected Tools**:
- get_job_status - Check status of submitted jobs
- get_job_result - Get results from completed jobs
- get_job_log - View log output from jobs
- cancel_job - Cancel running jobs
- list_jobs - List all submitted jobs
- submit_conformational_sampling - Submit single sequence conformational sampling
- submit_batch_processing - Submit multiple sequence batch processing
- validate_peptide_sequence - Validate peptide sequences
- check_adcp_binary - Check ADCP binary availability
- get_server_info - Get server information and capabilities

### Prompt 2: Server Information
"Use get_server_info to show me details about the adcp-tools server capabilities and configuration."

**Expected Response**:
- Server name: adcp-cycpep-tools
- Version: 1.0.0
- API type: submit_only
- Binary status: available
- Jobs directory path
- Scripts directory path

### Prompt 3: Binary Check
"Check if the ADCP binary is available and accessible using check_adcp_binary."

**Expected Response**:
- Status: available
- Binary path shown
- Binary size information
- Success message

## Utility Tools Tests

### Prompt 4: Sequence Validation - Valid
"Validate this peptide sequence for ADCP processing: 'GRGDSP'"

**Expected Response**:
- Status: valid
- Sequence: GRGDSP (uppercase)
- Length: 6 amino acids
- Success message

### Prompt 5: Sequence Validation - Invalid Length
"Validate this peptide sequence: 'GPGP' (too short)"

**Expected Response**:
- Status: invalid
- Error: Sequence too short (minimum 6 amino acids)

### Prompt 6: Sequence Validation - Invalid Characters
"Validate this peptide sequence: 'GRGDSP123' (contains numbers)"

**Expected Response**:
- Status: invalid
- Error: Invalid amino acids: 1, 2, 3

### Prompt 7: Sequence Validation - Too Long
"Validate this peptide sequence: 'GPGPGPGPGPGPGPGPGPGPG' (21 amino acids, too long)"

**Expected Response**:
- Status: invalid
- Error: Sequence too long (maximum 20 amino acids)

## Submit API Tests - Conformational Sampling

### Prompt 8: Submit Basic Conformational Sampling
"Submit a conformational sampling job for the cyclic peptide sequence 'GRGDSP' with default parameters."

**Expected Response**:
- Status: submitted
- Job ID returned (8 character string)
- Message with instructions to use get_job_status

### Prompt 9: Submit with Custom Parameters
"Submit conformational sampling for 'GPGPGP' with 10 runs and 100000 steps, name it 'test_peptide'."

**Expected Response**:
- Status: submitted
- Job ID returned
- Message confirming submission

### Prompt 10: Submit Disulfide Peptide
"Submit conformational sampling for the disulfide-bridged peptide 'CGPGPC' with disulfide constraints enabled."

**Expected Response**:
- Status: submitted
- Job ID returned
- Disulfide constraints should be enabled

### Prompt 11: Submit Invalid Sequence
"Try to submit conformational sampling for invalid sequence 'INVALID123'."

**Expected Response**:
- Status: error
- Error message about invalid sequence
- No job submitted

## Submit API Tests - Batch Processing

### Prompt 12: Submit Batch Job
"Submit a batch processing job using the file 'examples/data/sequences/batch_sequences.txt' with 2 max workers."

**Expected Response**:
- Status: submitted
- Job ID returned
- Message about batch job submission

### Prompt 13: Submit Batch with Invalid File
"Try to submit batch processing with non-existent file 'nonexistent.txt'."

**Expected Response**:
- Status: error
- Error message about file not found
- No job submitted

## Job Management Tests

### Prompt 14: Check Job Status
"Check the status of job '<job_id>' from a previous submission."

**Expected Responses** (varies by timing):
- Status: pending/running/completed/failed
- Job ID and name shown
- Timestamps for submission, start, completion
- Error details if failed

### Prompt 15: List All Jobs
"List all submitted jobs regardless of status."

**Expected Response**:
- Status: success
- Array of jobs with ID, name, status, submission time
- Total count shown
- Jobs sorted by newest first

### Prompt 16: List Only Completed Jobs
"List all jobs with status 'completed'."

**Expected Response**:
- Status: success
- Only completed jobs shown
- Filtered list with completion details

### Prompt 17: View Job Logs
"Show me the last 20 lines of logs for job '<job_id>'."

**Expected Response**:
- Status: success
- Job ID confirmed
- Log lines shown (up to 20)
- Total line count

### Prompt 18: Get Job Results
"Get the results from completed job '<job_id>'."

**Expected Responses**:
- If completed: Full results with output files, metadata
- If not completed: Error message with current status
- If failed: Error details

### Prompt 19: Cancel Running Job
"Cancel the running job '<job_id>'."

**Expected Response**:
- Status: success if job was running
- Error if job not found or not running
- Confirmation message

## End-to-End Workflow Tests

### Prompt 20: Full Workflow - Single Peptide
"I want to perform conformational sampling on the cyclic peptide 'GRGDSP'. Please:
1. First validate the sequence
2. Submit a conformational sampling job with 5 runs
3. Check the job status
4. Show me how to get the results when complete"

**Expected Flow**:
1. validate_peptide_sequence → valid result
2. submit_conformational_sampling → job ID returned
3. get_job_status → current status
4. Instructions for get_job_result when ready

### Prompt 21: Full Workflow - Batch Processing
"I want to process multiple cyclic peptides from the batch file. Please:
1. Check that the ADCP binary is available
2. Submit batch processing for 'examples/data/sequences/batch_sequences.txt' with 2 workers
3. Show me how to monitor progress"

**Expected Flow**:
1. check_adcp_binary → available status
2. submit_batch_processing → batch job ID
3. Instructions for get_job_log and get_job_status

### Prompt 22: Error Recovery Workflow
"I submitted a job with an invalid sequence. Show me:
1. What happens when I submit invalid data
2. How to check what went wrong
3. How to submit a corrected version"

**Expected Flow**:
1. Demonstrate validation error on submit
2. Show job status/log checking
3. Submit corrected sequence successfully

## Performance and Load Tests

### Prompt 23: Multiple Job Submissions
"Submit 3 different conformational sampling jobs in sequence:
- Job 1: 'GRGDSP' with 5 runs
- Job 2: 'GPGPGP' with 3 runs
- Job 3: 'CGPGPC' with disulfide constraints and 5 runs
Then list all jobs to see their status."

**Expected Response**:
- 3 successful submissions with different job IDs
- list_jobs shows all 3 jobs
- Each job has appropriate parameters

### Prompt 24: Job Queue Management
"After submitting several jobs, show me:
1. How many total jobs are in the system
2. How many are running, pending, completed
3. The oldest and newest submissions"

**Expected Response**:
- Comprehensive job list with status breakdown
- Proper sorting by submission time
- Status distribution summary

## Error Handling and Edge Cases

### Prompt 25: Missing Binary Scenario
"What happens if the ADCP binary is missing when I try to submit a job?"

**Expected Response**:
- Error message about binary not found
- Specific paths searched
- Clear instructions for resolution

### Prompt 26: Invalid Job ID Handling
"Try to get status for a non-existent job ID 'invalid123'."

**Expected Response**:
- Status: error
- Clear error message about job not found
- No crash or unexpected behavior

### Prompt 27: Long Sequence Edge Case
"Try to submit conformational sampling for a 20-amino acid sequence (maximum length)."

**Expected Response**:
- Should accept if valid amino acids
- Warning about longer computation time
- Successful submission

## Integration Verification

### Prompt 28: Tool Availability Check
"Verify that all expected ADCP tools are available and working by listing them and testing one from each category."

**Expected Response**:
- All 10 tools listed and callable
- At least one successful test from each category:
  - Job management (e.g., list_jobs)
  - Submit tools (e.g., basic conformational sampling)
  - Utilities (e.g., validate_peptide_sequence)

### Prompt 29: End-to-End Data Flow
"Demonstrate the complete data flow from sequence input to results retrieval using a simple test case."

**Expected Response**:
- Complete workflow demonstration
- Clear progression through all stages
- Actual data shown at each step

### Prompt 30: Production Readiness Check
"Is this ADCP MCP server ready for production use? Check all critical components."

**Expected Response**:
- Binary availability confirmed
- Job management functional
- Error handling robust
- Documentation complete
- All tools tested and working

---

## Test Execution Notes

**Important**: These tests should be run with the adcp-tools MCP server registered in Claude Code or Gemini CLI.

**Test Data**: Use the provided batch_sequences.txt file for batch testing.

**Timing**: Some jobs may take 20-60 minutes to complete, so status checking and result retrieval may need to be tested in separate sessions.

**Expected Failures**: Some prompts are designed to test error handling (invalid sequences, missing files, etc.) - these should fail gracefully with helpful error messages.

**Job IDs**: Replace `<job_id>` with actual job IDs returned from submit operations.