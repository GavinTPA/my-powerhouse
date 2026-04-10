# GHL Email Template Standard

Approved email styling. Use this as the base for ALL outbound GHL emails.

**Origin:** RRM Team Meeting Agenda email (2026-03-02). Ed: "I REALLY LIKE THE LOOK AND FEEL OF THAT EMAIL."

---

## Base Container

```html
<div style="font-family: Arial, Helvetica, sans-serif; max-width: 600px; margin: 0 auto; color: #333333; line-height: 1.6;">
  <!-- email content here -->
</div>
```

## Section Dividers

```html
<hr style="border: none; border-top: 1px solid #dddddd; margin: 20px 0;">
```

## Section Headers

```html
<h2 style="color: #222222; font-size: 18px; margin-bottom: 10px;">Section Title</h2>
```

## Agenda / Data Tables

Alternating row backgrounds, clean borders:

```html
<table style="width: 100%; border-collapse: collapse; font-size: 14px;">
  <tr style="background-color: #f5f5f5;">
    <td style="padding: 8px 12px; border: 1px solid #ddd; width: 80px;"><strong>Label</strong></td>
    <td style="padding: 8px 12px; border: 1px solid #ddd;">Content</td>
  </tr>
  <tr>
    <td style="padding: 8px 12px; border: 1px solid #ddd;"><strong>Label</strong></td>
    <td style="padding: 8px 12px; border: 1px solid #ddd;">Content</td>
  </tr>
</table>
```

## CTA Button (Orange)

```html
<p style="margin: 15px 0;">
  <a href="URL" style="display: inline-block; background-color: #E8620A; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; font-size: 14px;">Button Text</a>
</p>
```

## Fine Print / Subtle Text

```html
<p style="font-size: 13px; color: #666666;">Subtle instruction or note.</p>
```

## Bullet Lists

```html
<ul style="padding-left: 20px;">
  <li>Item one</li>
  <li>Item two</li>
</ul>
```

## Key Principles

| Element | Style |
|---------|-------|
| Font | Arial, Helvetica, sans-serif |
| Max width | 600px centered |
| Body text color | #333333 |
| Heading color | #222222 |
| Line height | 1.6 |
| Table rows | Alternating #f5f5f5 / white |
| Table borders | 1px solid #ddd |
| CTA button | #E8620A (neon-marillion orange) |
| Section dividers | 1px solid #dddddd, 20px margin |
| Fine print | 13px, #666666 |

## Usage

When creating ANY GHL email (meeting agendas, member updates, course announcements, etc.):

1. Start with the base container div
2. Use section headers + dividers between topics
3. Use the agenda table for structured content
4. Use the orange CTA button for downloads or links
5. Close with your name — no formal signature block needed
6. All CSS must be inline (GHL strips `<style>` tags)
