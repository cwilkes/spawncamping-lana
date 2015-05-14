-- http://en.wikipedia.org/wiki/Bloom_filter#Approximating_the_number_of_items_in_a_Bloom_filter

-- these MUST be the same as in bf.lua
local m = 10000000
local n = 1000000
local k = math.ceil((m/n)*math.log(2))

local function find_ns_cat_site_keys(partner_id, ns, category)
    local perm_key        = 'perms/partner:' .. partner_id
    local cat_site_key    = 'cat_site/ns:' .. ns .. ':cat:' .. category
    local available_sites = redis.call('sinter', perm_key, cat_site_key)
    local nscat_keys = {}
    for j=1,#available_sites do
        nscat_keys[#nscat_keys+1] = 'bf/ns:' .. ns .. ':cat:' .. category .. ':site:' .. available_sites[j]
    end
    return nscat_keys
end

local function make_tmp_fn(prefix, partner_id, vals)
    local ret = 'tmp/'
    ret = ret .. prefix .. '_'
    ret = ret .. partner_id
    for j=1,#vals do
        ret = '_' .. vals[j]
    end
    return ret
end

local function bitop_and(key, vals)
    return redis.call('BITOP', 'AND', key, unpack(vals))
end

local function bitop_or(key, vals)
    return redis.call('BITOP', 'OR', key, unpack(vals))
end

local function make_cache_cat_hits_key(partner_id, ns, category)
    local ns_cat_site_keys = find_ns_cat_site_keys(partner_id, ns, category)
    local cache_cat_hits_key = 'cache/ns:' .. ns .. ':cat:' .. category .. ':partner:' .. partner_id
    bitop_or(cache_cat_hits_key, ns_cat_site_keys)
    return cache_cat_hits_key
end

local function make_category_hits(partner_id, ns_cats)
    local cat_keys = {}
    for i=1,#ns_cats,2 do
        cat_keys[#cat_keys+1] = make_cache_cat_hits_key(partner_id, ns_cats[i], ns_cats[i+1])
    end
    return cat_keys
end

local function item_estimate(on_bitcount)
    local nominator = m * math.log(1 - on_bitcount/m)
    return math.ceil(-nominator/k)
end

local function do_bitop(op_type, partner_id, vals)
    local key = make_tmp_fn(op_type, partner_id, vals)
    if op_type == 'or' then
        bitop_or(key, vals)
    else
        bitop_and(key, vals)
    end
    local count = redis.call('bitcount', key)
    redis.call('del', key)
    return count
end

local partner_id = KEYS[1]
local cat_keys = make_category_hits(partner_id, ARGV)

local and_count = do_bitop('and', partner_id, cat_keys)
local or_count  = do_bitop('or',  partner_id, cat_keys)

return  'raw=(' .. and_count .. ',' .. or_count .. '), estimate=(' .. item_estimate(and_count) .. ',' .. item_estimate(or_count) .. ')'
