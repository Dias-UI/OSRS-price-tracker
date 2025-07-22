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
Gui, +LastFound +AlwaysOnTop -Caption +ToolWindow
Gui, Color, FFFFFF
WinSet, TransColor, FFFFFF 220
Gui, Font, s10 c00FFFF, Consolas ; Cyan text
Gui, Add, Text, vOSRSText w500 h250 Left, Initializing...

SysGet, MonitorWorkArea, MonitorWorkArea
GuiWidth := 500
GuiHeight := 250
xPos := MonitorWorkAreaRight - GuiWidth - 150 ; Moved further to the left
yPos := MonitorWorkAreaTop + 50
Gui, Show, x%xPos% y%yPos% w%GuiWidth% h%GuiHeight%

GoSub, UpdateData
Return

AddCommas(number) {
    return RegExReplace(number, "\G\d+?(?=(?:\d{3})++(?>\.|$))", "$0,")
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
    items := []
    items.Push({name: "Torstol Seed",     ref: 13333,    url: "https://secure.runescape.com/m=itemdb_oldschool/Torstol+seed/viewitem?obj=5304"})
    items.Push({name: "Sunfire Splint",   ref: 270,      url: "https://secure.runescape.com/m=itemdb_oldschool/Sunfire+splinters/viewitem?obj=28924"})
    items.Push({name: "Dragon Pickaxe",   ref: 900000,   url: "https://secure.runescape.com/m=itemdb_oldschool/Dragon+pickaxe/viewitem?obj=11920"})
    items.Push({name: "Anglerfish",       ref: 1440,     url: "https://secure.runescape.com/m=itemdb_oldschool/Anglerfish/viewitem?obj=13441"})
    items.Push({name: "Lightbearer",      ref: 6000000,  url: "https://secure.runescape.com/m=itemdb_oldschool/Lightbearer/viewitem?obj=25975"})
    items.Push({name: "Osmumten's Fang",  ref: 30000000, url: "https://secure.runescape.com/m=itemdb_oldschool/Osmumten%27s+fang/viewitem?obj=26219"})
    whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")

    for index, item in items
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
            sign := change >= 0 ? "+" : ""
            changeStr := sign . change . "%"
            
            if (DebugMode)
                OutputDebug, %itemName%: Final price=%currentPrice%, change=%changeStr%
        }

        line := LeftAlign(item.name, w_item)
              . CenterAlign(currentPrice = "N/A" ? "N/A" : AddCommas(currentPrice), w_curr)
              . CenterAlign(AddCommas(refPrice), w_ref)
              . CenterAlign(changeStr, w_chg)
        
        displayText .= line . "`n"
    }

    GuiControl,, OSRSText, %displayText%
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
