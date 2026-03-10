const axios = require("axios")

const MT5 = "http://127.0.0.1:5001"

const placedOrders = new Set()

const array_point = [
  5582, 5552, 5522, 5492, 5462, 5432, 5402, 5372, 5342, 5312,
  5282, 5252, 5222, 5192, 5162, 5132, 5102, 5072, 5042, 5012,
  4982, 4952, 4922
];

setInterval(async () => {

    try{
        await managePositions()
        // await cleanupPlacedOrders()
        // await processPrice()
    }catch(err){
        console.log("BOT ERROR:",err.message)
        if(err.response) {
            console.log("Response status:", err.response.status)
            console.log("Response data:", err.response.data)
            console.log("Request URL:", err.config?.url)
        }
    }

},200)

async function getPrice(symbol) {
    const res = await axios.get(`${MT5}/price/${symbol}`)

    return res.data
}

async function buy(symbol, lot) {
    const res = await axios.post(`${MT5}/buy`, {
        symbol,
        lot
    })

    console.log("BUY RESULT:", res.data)
}


async function buyLimit(symbol, lot, price, sl, tp) {
    const res = await axios.post(`${MT5}/buy-limit`, {
        symbol,
        lot,
        price,
        sl,
        tp
    })

    console.log("BUY LIMIT RESULT:", res.data)
}

async function sellLimit(symbol, lot, price, sl, tp) {
    const res = await axios.post(`${MT5}/sell-limit`, {
        symbol,
        lot,
        price,
        sl,
        tp
    })

    console.log("SELL LIMIT RESULT:", res.data)
}

async function sell(symbol, lot) {
    const res = await axios.post(`${MT5}/sell`, {
        symbol,
        lot
    })

    console.log("SELL RESULT:", res.data)
}

async function balance() {
    const res = await axios.get(`${MT5}/balance`)
    console.log(res.data)
}

async function getOrders() {
    const res = await axios.get(`${MT5}/orders`)
    return res.data
}

async function getPositions() {
    const res = await axios.get(`${MT5}/positions`)
    return res.data
}

async function modifySL(ticket, sl) {
    const res = await axios.get(`${MT5}/modify-sl`, {
        params: { ticket, sl }
    })
    return res.data
}

async function managePositions() {
    const positions = await getPositions()
    
    for(const pos of positions) {
        const entry = pos.price_open
        const currentSL = pos.sl || 0
        const currentTP = pos.tp || 0
        const symbol = pos.symbol
        const type = pos.type // 0 = BUY, 1 = SELL
        
        // Nếu SL đã ở entry rồi thì skip
        if(Math.abs(currentSL - entry) <= 0.5) {
            continue
        }
        
        // Lấy giá hiện tại
        const priceData = await getPrice(symbol)
        const currentPrice = type === 0 ? priceData.bid : priceData.ask
        
        // Kiểm tra giá đã lãi >= 3 points
        let profitReached = false
        
        if(type === 0) { // BUY
            profitReached = currentPrice >= entry + 3
        } else { // SELL
            profitReached = currentPrice <= entry - 3
        }
        
        // Nếu đã lãi 3 points thì dịch SL về entry
        if(profitReached) {
            console.log(`MOVE SL TO BREAKEVEN: Ticket ${pos.ticket}, Entry: ${entry}, Current: ${currentPrice}`)
            await modifySL(pos.ticket, entry)
        }
    }
}

// async function cleanupPlacedOrders() {
//     // Lấy danh sách lệnh pending hiện tại
//     const orders = await getOrders()
    
//     // Tạo Set chứa các orderKey còn tồn tại
//     const existingOrders = new Set()
    
//     for(const order of orders) {
//         if(order.type === 2) { // BUY_LIMIT
//             existingOrders.add(`BUY_${order.price_open}`)
//         } else if(order.type === 3) { // SELL_LIMIT
//             existingOrders.add(`SELL_${order.price_open}`)
//         }
//     }
    
//     // Xóa các orderKey không còn tồn tại (đã filled hoặc bị hủy)
//     for(const orderKey of placedOrders) {
//         if(!existingOrders.has(orderKey)) {
//             console.log("REMOVE ORDER:", orderKey)
//             placedOrders.delete(orderKey)
//         }
//     }
// }

// async function processPrice() {

//     const symbol = "XAUUSDm"

//     const priceData = await getPrice(symbol)
//     const price = priceData.ask

//     // console.log("CURRENT PRICE:", price)

//     for(let i = 0; i < array_point.length - 1; i++){

//         const a = array_point[i]
//         const b = array_point[i+1]

//         // giá nằm giữa 2 vùng
//         if(price <= a && price >= b){

//             // console.log(`PRICE BETWEEN ${a} - ${b}`)

//             const checkTouched = await axios.get(
//                 `${MT5}/check-price-touched`,
//                 {
//                     params:{
//                         symbol,
//                         hours:8,
//                         price:a
//                     }
//                 }
//             )

//             if(checkTouched.data.touched){

//                 const orderKey = `BUY_${b}`

//                 if(!placedOrders.has(orderKey)){

//                     console.log("PLACE BUY LIMIT:", b)

//                     await buyLimit(symbol,0.02,b,b-11,b+9)

//                     placedOrders.add(orderKey)
//                 }

//                 return
//             }

//             const checkTouchedB = await axios.get(
//                 `${MT5}/check-price-touched`,
//                 {
//                     params:{
//                         symbol,
//                         hours:8,
//                         price:b
//                     }
//                 }
//             )

//             if(checkTouchedB.data.touched){

//                 const orderKey = `SELL_${a}`

//                 if(!placedOrders.has(orderKey)){

//                     console.log("PLACE SELL LIMIT:", a)

//                     await sellLimit(symbol, 0.02, a, a+11, a-9)

//                     placedOrders.add(orderKey)
//                 }

//                 return
//             }

//         }

//     }

// }

// async function runBot() {

//     const symbol = "XAUUSDm"

//     const price = await getPrice(symbol)

//     console.log("PRICE:", price)

//     if(price.ask < 5192){
//         await buyLimit(symbol,0.01, 5132, 5100, 5250)
//     }else{
//         await sell(symbol,0.01)
//     }

// }

// runBot()