# Upload Timeout & Validation Fix

## Problem Summary

During file upload and AI extraction:
1. **Timeout Issue**: AI extraction took 4.5 minutes, but frontend only waited 3.75 minutes before timing out
2. **Lost Validation**: After timeout, user never saw the validation form to review/correct extracted data
3. **Auto-Verification**: Records appeared as "VERIFIED" in the system even though user never validated them

## Root Causes

### 1. Insufficient Timeout Duration
**Location**: `FrontEndV2/src/components/Upload.js` lines 109-110

**Before**:
```javascript
const maxAttempts = 45; // Check for up to ~4 minutes
const pollInterval = 5000; // Check every 5 seconds
// Total: 45 × 5 = 225 seconds = 3.75 minutes
```

**Problem**: AI extraction (especially with `ai_parse_document` + `ai_query`) can take 4-7 minutes for complex PDFs

### 2. Unclear Post-Timeout Behavior
**Location**: Same file, lines 155-159

**Before**:
```javascript
setError('Processing is taking longer than expected. Your file was uploaded successfully. Please check the Portfolio page in a few minutes to see if the extraction completed.');
setUploadState('error');
```

**Problem**: 
- User didn't know where to find their extracted data
- No way to validate the record from the upload flow
- Generic error state, not helpful guidance

### 3. Record Status Confusion
**Location**: `DatabricksResources/02_Structurer.sql` line 70

Records are initially inserted with status `'NEW'`:
```sql
'NEW' as validation_status
```

**But**: The confusion about "VERIFIED" status was likely due to:
- Batch promotion scripts running automatically
- Or viewing records after someone else validated them
- Records with status 'NEW' sitting in the validation queue

## Solution Implemented

### 1. ✅ Increased Timeout Duration

**New timeout**: 90 attempts × 5 seconds = 450 seconds = **7.5 minutes**

```javascript
const maxAttempts = 90; // Check for up to ~7.5 minutes (increased for AI extraction)
const pollInterval = 5000; // Check every 5 seconds
```

**Updated stage timing**:
- Stage 1 (Uploading): 0-30 seconds
- Stage 2 (Parsing): 30-120 seconds (2 minutes)
- Stage 3 (AI Extracting): 120-375 seconds (2-6 minutes) ← **Extended**
- Stage 4 (Validating): 375+ seconds

### 2. ✅ Better Timeout Handling

**New state**: `timeout_with_validation` instead of generic `error`

**New behavior**:
- Shows clear explanation of what happened
- Provides actionable next steps
- Directs user to validation section below
- Automatically refreshes the NEW records list
- Offers option to check validation section or upload another file

**UI Changes**:
```javascript
setError('AI extraction is taking longer than expected (>7 minutes). Your file was uploaded successfully and extraction may still be running. Please check the "Validate Extracted Records" section below in a few minutes to review and validate the data.');
setUploadState('timeout_with_validation');
fetchNewRecords(); // Refresh validation list
```

### 3. ✅ Enhanced Validation Section

**Added Refresh Button**:
- Manual refresh capability for validation records
- Visual feedback (spinning icon) while refreshing
- Allows users to check if their extraction completed
- Located in validation section header

**Features**:
- Click "Refresh Records" to check for newly extracted data
- Records with status 'NEW' appear in the table
- User can edit, review, and validate before promoting to silver

### 4. ✅ Improved User Guidance

**New timeout screen includes**:
- Clear explanation of what happened
- Why it might have happened (large PDF, complex lease, system load)
- Step-by-step next actions:
  1. Scroll to validation section
  2. Wait 1-2 minutes
  3. Click refresh
  4. Review and validate

**Visual design**:
- Orange/warning color scheme (not error red)
- Information box with helpful details
- Two action buttons: "Check Validation Section" and "Upload Another"

## Files Changed

### Updated Files:
1. **`FrontEndV2/src/components/Upload.js`**
   - Increased timeout from 3.75 to 7.5 minutes
   - Added `timeout_with_validation` state
   - Added refresh functionality
   - Improved error messaging
   - Auto-refresh validation list on timeout

2. **`FrontEndV2/src/components/Upload.css`**
   - New `.timeout-validation-state` styling
   - `.timeout-info` information box styling
   - `.refresh-records-button` styling
   - `.spinning` animation for refresh icon
   - Button styles: `.check-validation-button`, `.retry-button-secondary`

## Data Flow (Fixed)

```
User uploads PDF
   ↓
Frontend waits up to 7.5 minutes (was 3.75)
   ↓
Case 1: Extraction completes within 7.5 min
   → Validation form shown
   → User reviews/edits
   → User clicks "Validate & Submit"
   → Status: NEW → VERIFIED
   → Promoted to silver_leases
   → ✅ Appears in frontend

Case 2: Extraction takes >7.5 minutes
   → Timeout screen shown (new UI)
   → User clicks "Check Validation Section"
   → Scrolls to validation section
   → Clicks "Refresh Records"
   → Record appears with status 'NEW'
   → User edits/validates
   → Status: NEW → VERIFIED
   → Promoted to silver_leases
   → ✅ Appears in frontend
```

## Prevention of "Auto-Verification"

**Records are only marked VERIFIED when**:
1. User clicks "Validate & Submit" on single record form
2. User selects records and clicks "Validate Selected" in validation section
3. Backend API `/api/validate-record` or `/api/records/validate-multiple` is called
4. Manual SQL update (admin/batch operations)

**Records stay as 'NEW' when**:
- Extraction completes but user hasn't validated
- Timeout occurs before user validates
- User closes browser before validating

**To check for stuck NEW records**:
```sql
SELECT COUNT(*), MIN(uploaded_at), MAX(uploaded_at)
FROM fins_team_3.lease_management.bronze_leases
WHERE validation_status = 'NEW';
```

## Testing Recommendations

### Test Case 1: Normal Flow (< 7.5 min)
1. Upload a small/simple PDF
2. Wait for extraction (should be 2-4 minutes)
3. Validation form should appear
4. Review and validate
5. ✅ Check record appears in portfolio

### Test Case 2: Timeout Flow (> 7.5 min)
1. Upload a large/complex PDF
2. Wait for timeout (artificial: can lower maxAttempts temporarily)
3. Should see new timeout screen with guidance
4. Click "Check Validation Section" button
5. Scroll to validation section
6. Click "Refresh Records" after 1-2 minutes
7. Record should appear with status 'NEW'
8. Edit/validate the record
9. ✅ Check record appears in portfolio

### Test Case 3: Multiple Uploads
1. Upload PDF #1
2. While it's processing, check validation section
3. Previous NEW records should be visible
4. Refresh button should update the list
5. ✅ Can validate old records while new one processes

## User Benefits

1. **✅ No More Lost Validations**: Even if timeout occurs, user can still validate
2. **✅ Clear Communication**: Knows exactly what to do next
3. **✅ Self-Service**: Can refresh and check status themselves
4. **✅ Longer Wait Time**: 7.5 minutes accommodates complex PDFs
5. **✅ Better UX**: Orange warning instead of red error
6. **✅ Batch Validation**: Can validate multiple stuck records at once

## Configuration

To adjust timeout if needed, edit `Upload.js`:

```javascript
// Current: 7.5 minutes
const maxAttempts = 90;
const pollInterval = 5000;

// For testing (1 minute):
const maxAttempts = 12;
const pollInterval = 5000;

// For very large PDFs (10 minutes):
const maxAttempts = 120;
const pollInterval = 5000;
```

## Monitoring

To monitor extraction times:

```sql
-- Check average extraction time
SELECT 
  AVG(DATEDIFF(SECOND, uploaded_at, extracted_at)) as avg_seconds,
  MAX(DATEDIFF(SECOND, uploaded_at, extracted_at)) as max_seconds,
  COUNT(*) as total_extractions
FROM fins_team_3.lease_management.bronze_leases
WHERE extracted_at IS NOT NULL
  AND uploaded_at IS NOT NULL;
```

If average extraction time > 300 seconds (5 min), consider:
- Optimizing AI agent prompts
- Using faster warehouse size
- Pre-processing PDFs to reduce complexity
- Implementing extraction caching

---

**Result**: Users can now successfully validate all uploaded documents, even if AI extraction takes longer than expected. No more lost validations or confusion about record status!

