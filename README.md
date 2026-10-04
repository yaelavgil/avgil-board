# לוח של האבגילים המשפצים

לוח המשימות המשותף של יעל ורועי — שיפוץ אשל 57, בית, בית ספר ובריאות.

**האפליקציה:** https://yaelavgil.github.io/avgil-board

## איך זה עובד

- עמוד אחד, `index.html`, בלי שלב בנייה ובלי תלויות.
- המשימות נשמרות ב-Firebase Realtime Database תחת `/board/tasks/<id>` — אותו פרויקט שמשרת את `lighting-map` ו-`reno-payments`.
- סנכרון חי דרך Server-Sent Events: מה שאחד מסמן בטלפון שלו מופיע אצל השני תוך שנייה, בלי התחברות.
- העמוד נטען עם עותק מוטמע של המשימות כדי שהציור הראשון יהיה מיידי, ואז מתעדכן מהרשת.

## מבנה משימה

```
id, title, notes, cat, due, list, order, done, owner, ongoing, pin, waTo, wa, updatedAt
```

- `cat` — trip / reno / home / gift / idea / school / health
- `owner` — יעל / רועי / שנינו
- `ongoing: true` — משימה מתמשכת: קטגוריה משלה בראש הלוח, בלי תאריך יעד, אף פעם לא נספרת כאיחור.

## להוספה למסך הבית באייפון

Safari → שיתוף → הוספה למסך הבית.
