#NoEnv
#Warn
#SingleInstance Force
SendMode Input

; Auto-execute section
#Persistent
SetWorkingDir %A_ScriptDir%

; Debug mode - set to true to see extracted values
DebugMode := false

; Create GUI first
Gui, New
Gui, +LastFound +AlwaysOnTop -Caption +ToolWindow -Border
Gui, Color, 000000
WinSet, TransColor, 000000 220
Gui, Font, s10 c00FFFF, Consolas ; Cyan text
; Use standard Edit control with non-selectable properties
Gui, Add, Edit, vOSRSText w500 h350 Left ReadOnly -VScroll -HScroll -Wrap -Border -E0x200 Background000000, Initializing...
; Make it truly non-intrusive by removing selection capability
GuiControlGet, hEdit, Hwnd, OSRSText
; Disable text selection and make it non-focusable
SendMessage, 0x00B1, -1, -1,, ahk_id %hEdit% ; EM_SETSEL to deselect
WinSet, ExStyle, +0x200,, ahk_id %hEdit% ; WS_EX_NOACTIVATE - prevents activation

SysGet, MonitorWorkArea, MonitorWorkArea
GuiWidth := 500
GuiHeight := 350 ; Increased height for more items
xPos := MonitorWorkAreaRight - GuiWidth - 150 ; Moved further to the left
yPos := MonitorWorkAreaTop + 50
Gui, Show, x%xPos% y%yPos% w%GuiWidth% h%GuiHeight%

GoSub, UpdateData
Return

AddCommas(number) {
    return RegExReplace(number, "\G\d+?(?=(?:\d{3})+(?>\.|$))", "$0,")
}

; Function to format change text with color indicators and visual formatting
FormatChange(changeStr, change) {
    if (changeStr = "N/A")
        return changeStr
    
    ; Simplified arrows - just arrowheads
    if (change > 0)
        return "+" . changeStr . " ↑"  ; Positive with up arrow
    else if (change < 0)
        return changeStr . " ↓"  ; Negative with down arrow
    else
        return changeStr . " →"  ; Neutral with right arrow
}

; Function to set colored text (simplified approach)
SetColoredText(controlName, text) {
    ; For now, just set the text normally since RTF is complex in AHK v1
    ; The visual indicators (arrows) will still show the change direction
    GuiControl,, %controlName%, %text%
}

LeftAlign(str, width) {
    spaces := width - StrLen(str)
    return str . (spaces > 0 ? SubStr("                    ", 1, spaces) : "")
}

CenterAlign(str, width) {
    len := StrLen(str)
    if (len >= width)
        return SubStr(str, 1, width)
    
    padTotal := width - len
    padLeft := Floor(padTotal / 2)
    padRight := Ceil(padTotal / 2)
    
    spaces := "                    " ; A string of spaces
    return SubStr(spaces, 1, padLeft) . str . SubStr(spaces, 1, padRight)
}

UpdateData:
try {
    ; --- Column Widths ---
    w_item := 18, w_curr := 12, w_ref := 12, w_chg := 10

    ; --- Header ---
    header1 := LeftAlign("Item", w_item) . CenterAlign("Current", w_curr) . CenterAlign("Reference", w_ref) . CenterAlign("Change", w_chg)
    header2 := SubStr("--------------------------------------------------", 1, w_item + w_curr + w_ref + w_chg)
    displayText := header1 . "`n" . header2 . "`n"

    ; --- Item List ---
    ; Top priority items
    topItems := []
    topItems.Push({name: "Torstol Seed",     ref: 13333,    url: "https://secure.runescape.com/m=itemdb_oldschool/Torstol+seed/viewitem?obj=5304"})
    topItems.Push({name: "Dragon Pickaxe",   ref: 900000,   url: "https://secure.runescape.com/m=itemdb_oldschool/Dragon+pickaxe/viewitem?obj=11920"})
    topItems.Push({name: "Anglerfish",       ref: 1440,     url: "https://secure.runescape.com/m=itemdb_oldschool/Anglerfish/viewitem?obj=13441"})
    topItems.Push({name: "Blighted Ice Sack", ref: 272,    url: "https://secure.runescape.com/m=itemdb_oldschool/Blighted+ancient+ice+sack/viewitem?obj=24607"})
    topItems.Push({name: "Dragon Arrow", ref: 1400, url: "https://secure.runescape.com/m=itemdb_oldschool/Dragon+arrow/viewitem?obj=11212"})
    
    ; Other items
    otherItems := []
    otherItems.Push({name: "Bond",             ref: 12000000, url: "https://secure.runescape.com/m=itemdb_oldschool/Old+school+bond/viewitem?obj=13190"})
    otherItems.Push({name: "Spirit Shield",   ref: 55000,    url: "https://secure.runescape.com/m=itemdb_oldschool/Spirit+shield/viewitem?obj=12829"})
    otherItems.Push({name: "Black Chinchompa", ref: 2500,   url: "https://secure.runescape.com/m=itemdb_oldschool/Black+chinchompa/viewitem?obj=11959"})
    otherItems.Push({name: "Purple Sweets",   ref: 6000,     url: "https://secure.runescape.com/m=itemdb_oldschool/Purple+sweets/viewitem?obj=10476"})
    otherItems.Push({name: "Magic Seed",      ref: 80000,    url: "https://secure.runescape.com/m=itemdb_oldschool/Magic+seed/viewitem?obj=5316"})
    otherItems.Push({name: "Granite Maul",    ref: 300000,   url: "https://secure.runescape.com/m=itemdb_oldschool/Granite+maul/viewitem?obj=4153"})
    otherItems.Push({name: "Ornate Maul Handle", ref: 420000, url: "https://secure.runescape.com/m=itemdb_oldschool/Ornate+maul+handle/viewitem?obj=24229"})
    otherItems.Push({name: "Sunfire Splinters",  ref: 270,      url: "https://secure.runescape.com/m=itemdb_oldschool/Sunfire+splinters/viewitem?obj=28924"})
    otherItems.Push({name: "Lightbearer",     ref: 5000000,  url: "https://secure.runescape.com/m=itemdb_oldschool/Lightbearer/viewitem?obj=25975"})
    otherItems.Push({name: "Osmumten's Fang", ref: 20000000, url: "https://secure.runescape.com/m=itemdb_oldschool/Osmumten%27s+fang/viewitem?obj=26219"})
    otherItems.Push({name: "Sanguinesti Staff", ref: 70000000, url: "https://secure.runescape.com/m=itemdb_oldschool/Sanguinesti+staff+%28uncharged%29/viewitem?obj=22481"})
    otherItems.Push({name: "Moonlight Bolts", ref: 200, url: "https://secure.runescape.com/m=itemdb_oldschool/Moonlight+antler+bolts/viewitem?obj=28878"})
    otherItems.Push({name: "Blood Rune", ref: 300, url: "https://secure.runescape.com/m=itemdb_oldschool/Blood+rune/viewitem?obj=565"})
    whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")

    ; Process top items first
    for index, item in topItems
    {
        try {
            whr.Open("GET", item.url, true)
            whr.SetRequestHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            whr.Send()
            whr.WaitForResponse(10000)  ; 10 second timeout
            html := whr.ResponseText
            
            if (StrLen(html) < 100) {
                throw Exception("Response too short, likely failed request")
            }
        } catch e {
            itemName := item.name
            errorMsg := e.message
            if (DebugMode)
                OutputDebug, %itemName%: Network error - %errorMsg%
            
            line := LeftAlign(item.name, w_item)
                  . CenterAlign("ERROR", w_curr)
                  . CenterAlign(AddCommas(item.ref), w_ref)
                  . CenterAlign("N/A", w_chg)
            displayText .= line . "`n"
            continue
        }

        ; Try multiple regex patterns to extract the current price
        currentPrice := ""
        debugInfo := ""
        
        ; Pattern 1: Look for title attribute with price - most comprehensive pattern
        if (RegExMatch(html, "i)<h3[^>]*>Current Guide Price[^<]*<span[^>]*title\s*=\s*[""']([0-9,]+)[""'][^>]*>", priceMatch)) {
            currentPrice := StrReplace(priceMatch1, ",", "")
            debugInfo := "Pattern 1 (title comprehensive): " . priceMatch1
        }
        
        ; Pattern 2: Simpler title pattern with flexible spacing
        if (currentPrice = "" && RegExMatch(html, "i)Current Guide Price.*?<span[^>]*title\s*=\s*[""']([0-9,]+)[""']", priceMatch)) {
            currentPrice := StrReplace(priceMatch1, ",", "")
            debugInfo := "Pattern 2 (title flexible): " . priceMatch1
        }
        
        ; Pattern 3: Look for title attribute anywhere in the span tag
        if (currentPrice = "" && RegExMatch(html, "i)<span[^>]*title\s*=\s*[""']([0-9,]+)[""'][^>]*>[^<]*</span>", priceMatch)) {
            currentPrice := StrReplace(priceMatch1, ",", "")
            debugInfo := "Pattern 3 (title anywhere): " . priceMatch1
        }
        
        ; Pattern 4: Extract from title attribute with any surrounding context
        if (currentPrice = "" && RegExMatch(html, "i)title\s*=\s*[""']([0-9,]+)[""']", priceMatch)) {
            ; Additional validation to ensure this is near "Current Guide Price"
            titlePos := RegExMatch(html, "i)title\s*=\s*[""']([0-9,]+)[""']")
            pricePos := RegExMatch(html, "i)Current Guide Price")
            if (titlePos > 0 && pricePos > 0 && Abs(titlePos - pricePos) < 500) {
                currentPrice := StrReplace(priceMatch1, ",", "")
                debugInfo := "Pattern 4 (title with validation): " . priceMatch1
            }
        }
        
        ; Pattern 5: ONLY as last resort - Look for span content directly (this might be the shortened value)
        if (currentPrice = "" && RegExMatch(html, "i)<h3[^>]*>Current Guide Price[^<]*<span[^>]*>([0-9,]+(?:\.[0-9]+)?[kmb]?)", priceMatch)) {
            ; Check if this looks like a shortened format (contains letters or decimals)
            if (RegExMatch(priceMatch1, "i)[kmb]") || RegExMatch(priceMatch1, "\.")) {
                ; This is likely a shortened format, skip it
                debugInfo := "Pattern 5 (span content - SKIPPED shortened format): " . priceMatch1
            } else {
                currentPrice := StrReplace(priceMatch1, ",", "")
                debugInfo := "Pattern 5 (span content - full number): " . priceMatch1
            }
        }
        
        ; Pattern 6: Last resort - any numeric value near "Current Guide Price" but only if it's a full number
        if (currentPrice = "" && RegExMatch(html, "i)Current Guide Price.*?([0-9,]{4,})", priceMatch)) {
            ; Only accept if it doesn't look like a shortened format
            if (!RegExMatch(priceMatch1, "i)[kmb]") && StrLen(StrReplace(priceMatch1, ",", "")) >= 3) {
                currentPrice := StrReplace(priceMatch1, ",", "")
                debugInfo := "Pattern 6 (nearby full number): " . priceMatch1
            }
        }
        
        ; Debug output
        itemName := item.name
        if (DebugMode && debugInfo != "")
            OutputDebug, %itemName%: %debugInfo% -> %currentPrice%
        
        ; Ensure currentPrice is numeric and valid
        if (currentPrice = "" || !RegExMatch(currentPrice, "^\d+$"))
        {
            if (DebugMode)
                OutputDebug, %itemName%: Failed to extract valid price, setting to N/A
            currentPrice := "N/A"
            changeStr := "N/A"
        }
        else
        {
            currentPrice := currentPrice + 0  ; Convert to number
            refPrice := item.ref
            change := Round(((currentPrice - refPrice) / refPrice) * 100, 2)
            changeStr := change . "%"
            changeFormatted := FormatChange(changeStr, change)
            
            if (DebugMode)
                OutputDebug, %itemName%: Final price=%currentPrice%, change=%changeStr%
        }

        line := LeftAlign(item.name, w_item)
              . CenterAlign(currentPrice = "N/A" ? "N/A" : AddCommas(currentPrice), w_curr)
              . CenterAlign(AddCommas(refPrice), w_ref)
              . CenterAlign(changeStr = "N/A" ? "N/A" : changeFormatted, w_chg)
        
        displayText .= line . "`n"
    }
    
    ; Add separator line
    separatorLine := SubStr("--------------------------------------------------", 1, w_item + w_curr + w_ref + w_chg)
    displayText .= separatorLine . "`n"
    
    ; Process other items
    for index, item in otherItems
    {
        try {
            whr.Open("GET", item.url, true)
            whr.SetRequestHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            whr.Send()
            whr.WaitForResponse(10000)  ; 10 second timeout
            html := whr.ResponseText
            
            if (StrLen(html) < 100) {
                throw Exception("Response too short, likely failed request")
            }
        } catch e {
            itemName := item.name
            errorMsg := e.message
            if (DebugMode)
                OutputDebug, %itemName%: Network error - %errorMsg%
            
            line := LeftAlign(item.name, w_item)
                  . CenterAlign("ERROR", w_curr)
                  . CenterAlign(AddCommas(item.ref), w_ref)
                  . CenterAlign("N/A", w_chg)
            displayText .= line . "`n"
            continue
        }

        ; Try multiple regex patterns to extract the current price
        currentPrice := ""
        debugInfo := ""
        
        ; Pattern 1: Look for title attribute with price - most comprehensive pattern
        if (RegExMatch(html, "i)<h3[^>]*>Current Guide Price[^<]*<span[^>]*title\s*=\s*[""']([0-9,]+)[""'][^>]*>", priceMatch)) {
            currentPrice := StrReplace(priceMatch1, ",", "")
            debugInfo := "Pattern 1 (title comprehensive): " . priceMatch1
        }
        
        ; Pattern 2: Simpler title pattern with flexible spacing
        if (currentPrice = "" && RegExMatch(html, "i)Current Guide Price.*?<span[^>]*title\s*=\s*[""']([0-9,]+)[""']", priceMatch)) {
            currentPrice := StrReplace(priceMatch1, ",", "")
            debugInfo := "Pattern 2 (title flexible): " . priceMatch1
        }
        
        ; Pattern 3: Look for title attribute anywhere in the span tag
        if (currentPrice = "" && RegExMatch(html, "i)<span[^>]*title\s*=\s*[""']([0-9,]+)[""'][^>]*>[^<]*</span>", priceMatch)) {
            currentPrice := StrReplace(priceMatch1, ",", "")
            debugInfo := "Pattern 3 (title anywhere): " . priceMatch1
        }
        
        ; Pattern 4: Extract from title attribute with any surrounding context
        if (currentPrice = "" && RegExMatch(html, "i)title\s*=\s*[""']([0-9,]+)[""']", priceMatch)) {
            ; Additional validation to ensure this is near "Current Guide Price"
            titlePos := RegExMatch(html, "i)title\s*=\s*[""']([0-9,]+)[""']")
            pricePos := RegExMatch(html, "i)Current Guide Price")
            if (titlePos > 0 && pricePos > 0 && Abs(titlePos - pricePos) < 500) {
                currentPrice := StrReplace(priceMatch1, ",", "")
                debugInfo := "Pattern 4 (title with validation): " . priceMatch1
            }
        }
        
        ; Pattern 5: ONLY as last resort - Look for span content directly (this might be the shortened value)
        if (currentPrice = "" && RegExMatch(html, "i)<h3[^>]*>Current Guide Price[^<]*<span[^>]*>([0-9,]+(?:\.[0-9]+)?[kmb]?)", priceMatch)) {
            ; Check if this looks like a shortened format (contains letters or decimals)
            if (RegExMatch(priceMatch1, "i)[kmb]") || RegExMatch(priceMatch1, "\.")) {
                ; This is likely a shortened format, skip it
                debugInfo := "Pattern 5 (span content - SKIPPED shortened format): " . priceMatch1
            } else {
                currentPrice := StrReplace(priceMatch1, ",", "")
                debugInfo := "Pattern 5 (span content - full number): " . priceMatch1
            }
        }
        
        ; Pattern 6: Last resort - any numeric value near "Current Guide Price" but only if it's a full number
        if (currentPrice = "" && RegExMatch(html, "i)Current Guide Price.*?([0-9,]{4,})", priceMatch)) {
            ; Only accept if it doesn't look like a shortened format
            if (!RegExMatch(priceMatch1, "i)[kmb]") && StrLen(StrReplace(priceMatch1, ",", "")) >= 3) {
                currentPrice := StrReplace(priceMatch1, ",", "")
                debugInfo := "Pattern 6 (nearby full number): " . priceMatch1
            }
        }
        
        ; Debug output
        itemName := item.name
        if (DebugMode && debugInfo != "")
            OutputDebug, %itemName%: %debugInfo% -> %currentPrice%
        
        ; Ensure currentPrice is numeric and valid
        if (currentPrice = "" || !RegExMatch(currentPrice, "^\d+$"))
        {
            if (DebugMode)
                OutputDebug, %itemName%: Failed to extract valid price, setting to N/A
            currentPrice := "N/A"
            changeStr := "N/A"
        }
        else
        {
            currentPrice := currentPrice + 0  ; Convert to number
            refPrice := item.ref
            change := Round(((currentPrice - refPrice) / refPrice) * 100, 2)
            changeStr := change . "%"
            changeFormatted := FormatChange(changeStr, change)
            
            if (DebugMode)
                OutputDebug, %itemName%: Final price=%currentPrice%, change=%changeStr%
        }

        line := LeftAlign(item.name, w_item)
              . CenterAlign(currentPrice = "N/A" ? "N/A" : AddCommas(currentPrice), w_curr)
              . CenterAlign(AddCommas(refPrice), w_ref)
              . CenterAlign(changeStr = "N/A" ? "N/A" : changeFormatted, w_chg)
        
        displayText .= line . "`n"
    }

    ; Use the new colored text function
    SetColoredText("OSRSText", displayText)
} catch e {
    GuiControl,, OSRSText, Error fetching OSRS data: %e%
}
return

!Esc::ExitApp
!r::Reload
!d::
    DebugMode := !DebugMode
    ToolTip, Debug Mode: %DebugMode%
    SetTimer, RemoveToolTip, 2000
    GoSub, UpdateData
return

RemoveToolTip:
    ToolTip
return

^+LButton::
MouseGetPos,,,,control
PostMessage, 0xA1, 2
return
