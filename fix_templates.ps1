# Get the content of the first template file
$file1 = "dashboard\templates\dashboard\weekly_product_meeting_detail.html"
$content1 = Get-Content $file1 -Raw

# Replace the meeting notes section
$pattern1 = '(<div class="card-body">\s+){{ meeting\.notes\|default:"No notes provided"\|linebreaks }}(\s+</div>)'
$replacement1 = '$1<div class="meeting-notes">
                        {{ meeting.notes|default:"No notes provided"|safe }}
                    </div>$2'
$newContent1 = $content1 -replace $pattern1, $replacement1

# Write the modified content back to the file
Set-Content -Path $file1 -Value $newContent1

# Get the content of the second template file
$file2 = "dashboard\templates\dashboard\weekly_meeting_detail.html"
$content2 = Get-Content $file2 -Raw

# Replace the meeting notes section
$pattern2 = '(<div class="card-body">\s+){{ meeting\.notes\|default:"No notes provided"\|linebreaks }}(\s+</div>)'
$replacement2 = '$1<div class="meeting-notes">
                        {{ meeting.notes|default:"No notes provided"|safe }}
                    </div>$2'
$newContent2 = $content2 -replace $pattern2, $replacement2

# Write the modified content back to the file
Set-Content -Path $file2 -Value $newContent2

# Get the content of the third template file
$file3 = "dashboard\templates\dashboard\weekly_product_meeting_detail_table.html"
$content3 = Get-Content $file3 -Raw

# Replace the meeting notes section
$pattern3 = '(<div class="card-body">\s+){{ meeting\.notes\|default:"No notes provided"\|linebreaks }}(\s+</div>)'
$replacement3 = '$1<div class="meeting-notes">
                        {{ meeting.notes|default:"No notes provided"|safe }}
                    </div>$2'
$newContent3 = $content3 -replace $pattern3, $replacement3

# Write the modified content back to the file
Set-Content -Path $file3 -Value $newContent3

Write-Output "All template files have been updated."