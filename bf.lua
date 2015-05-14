-- http://en.wikipedia.org/wiki/Xorshift

-- uint64_t s[2];
-- uint64_t xorshift128plus(void) {
-- 	uint64_t x = s[0];
--  uint64_t const y = s[1];
-- 	s[0] = y;
--  x ^= x << 23; // a
-- 	x ^= x >> 17; // b
-- 	x ^= y ^ (y >> 26); // c
-- 	s[1] = x;
--  return x + y;
-- }

-- http://en.wikipedia.org/wiki/Bloom_filter


-- m: number of bits in array
-- n: number of items to insert
-- k: number of hashes to do
-- m and n MUST remain the same for the same server
local m = 10000000
local n = 1000000
local k = math.ceil((m/n)*math.log(2))

local rand_const = 8675309


local s = {}
s[1] = 0 -- this gets replaced the first time through
s[2] = rand_const -- this needs to remain the same for consistant hashing

local function xorshift()
    local x = s[1]
    local y = s[2];
    s[1] = y
    local a = bit.bxor(x, bit.lshift(x, 23))
    local b = bit.bxor(a, bit.rshift(a, 17))
    local c = bit.bxor(b, bit.bxor(y, bit.rshift(y, 26)))
    s[2] = c
    return math.abs(c+y) % m
end

function string:split( inSplitPattern, outResults )
  if not outResults then
    outResults = { }
  end
  local theStart = 1
  local theSplitStart, theSplitEnd = string.find( self, inSplitPattern, theStart )
  while theSplitStart do
    table.insert( outResults, string.sub( self, theStart, theSplitStart-1 ) )
    theStart = theSplitEnd + 1
    theSplitStart, theSplitEnd = string.find( self, inSplitPattern, theStart )
  end
  table.insert( outResults, string.sub( self, theStart ) )
  return outResults
end

s[1] = KEYS[1]

for i=1,k do
    local offset = xorshift()
    for j=1,#ARGV do
        local nscat = ARGV[j]:split(",") -- ns, site, cat, freq, recency
        local key = "bf/ns:" .. nscat[1] .. ":cat:" .. nscat[3] .. ":site:" .. nscat[2]
        redis.call("SETBIT", key, offset, 1)
        redis.call("SADD", "cat_site/ns:" .. nscat[1] .. ":cat:" .. nscat[3], nscat[2])
    end
end

return #ARGV
