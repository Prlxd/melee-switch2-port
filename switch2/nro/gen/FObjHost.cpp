
// Generated from pinned doldecomp/melee fobj.c and spline.c; see generator for adaptations.
#include "PackedAnimation.h"
#include <cmath>
#include <cstring>
#include <stdexcept>
#include <cstddef>
namespace NativeMelee { namespace {
using u8=uint8_t; using u16=uint16_t; using u32=uint32_t;
using s8=int8_t; using s16=int16_t; using s32=int32_t; using f32=float;
struct HSD_FObj;
union HSD_ObjData { float fv; int iv; };
using HSD_ObjUpdateFunc = void(*)(void*, u8, HSD_ObjData*);
void HSD_FObjInterpretAnim(HSD_FObj*, void*, HSD_ObjUpdateFunc, float);
#define HSD_ASSERT(line, condition) if (!(condition)) throw std::runtime_error("animation state error")
#define HSD_A_OP_NONE 0
#define HSD_A_OP_CON 1
#define HSD_A_OP_LIN 2
#define HSD_A_OP_SPL0 3
#define HSD_A_OP_SPL 4
#define HSD_A_OP_SLP 5
#define HSD_A_OP_KEY 6

#define HSD_A_FRAC_FLOAT (0 << 5)
#define HSD_A_FRAC_S16 (1 << 5)
#define HSD_A_FRAC_U16 (2 << 5)
#define HSD_A_FRAC_S8 (3 << 5)
#define HSD_A_FRAC_U8 (4 << 5)

#define FOBJ_LOAD_DATA0 1
#define FOBJ_LOAD_DATA 2
#define FOBJ_LOAD_WAIT 3

#define TYPE_ROBJ 1
#define TYPE_JOBJ 12

struct HSD_FObj {
    struct HSD_FObj* next;
    u8* ad;
    u8* ad_head;
    u32 length;
    u8 flags;
    u8 op;
    u8 op_intrp;
    u8 obj_type;
    u8 frac_value;
    u8 frac_slope;
    u16 nb_pack;
    s16 startframe;
    u16 fterm;
    f32 time;
    f32 p0;
    f32 p1;
    f32 d0;
    f32 d1;
};

f32 splGetHelmite(f32 fterm, f32 time, f32 p0, f32 p1, f32 d0, f32 d1)
{
    f32 _3t2_T2;
    f32 _2t3_T3;
    f32 t3_T2;
    f32 t2_T;
    f32 t2;
    f32 _1_T2;

    _1_T2 = time * time;
    t2 = fterm * fterm;
    t2_T = _1_T2 * fterm;
    t3_T2 = t2 * (_1_T2 * time);
    _2t3_T3 = 2.0f * t3_T2 * fterm;
    _3t2_T2 = 3.0f * _1_T2 * t2;

    return (d1 * (t3_T2 - t2_T)) + ((d0 * (time + ((t3_T2 - t2_T) - t2_T))) +
                                    ((p0 * (1.0f + (_2t3_T3 - _3t2_T2))) +
                                     (p1 * (-_2t3_T3 + _3t2_T2))));
}

u32 HSD_FObjSetState(HSD_FObj* fobj, u32 state)
{
    if (fobj) {
        fobj->flags = (state & 0xF) | (fobj->flags & 0xF0);
    }
    return state;
}

u32 HSD_FObjGetState(HSD_FObj* fobj)
{
    if (!fobj) {
        return 0;
    }
    return fobj->flags & 0xF;
}

static inline void HSD_FObjReqAnim(HSD_FObj* fobj, f32 startframe)
{
    if (fobj == NULL) {
        return;
    }

    fobj->ad = fobj->ad_head;
    fobj->time = (f32) fobj->startframe + startframe;
    fobj->op = 0;
    fobj->op_intrp = 0;
    fobj->flags &= ~0x40;
    fobj->nb_pack = 0;
    fobj->fterm = 0;
    fobj->p0 = 0.f;
    fobj->p1 = 0.f;
    fobj->d0 = 0.f;
    fobj->d1 = 0.f;
    HSD_FObjSetState(fobj, 1);
}

void HSD_FObjReqAnimAll(HSD_FObj* fobj, f32 startframe)
{
    HSD_FObj* fp;

    if (fobj == NULL) {
        return;
    }

    for (fp = fobj; fp != NULL; fp = fp->next) {
        HSD_FObjReqAnim(fp, startframe);
    }
}

static inline void FObj_FlushKeyData(HSD_FObj* fobj, void* obj,
                                     HSD_ObjUpdateFunc obj_update, f32 rate)
{
    if (fobj->op_intrp == HSD_A_OP_KEY) {
        HSD_FObjInterpretAnim(fobj, obj, obj_update, rate);
    }
}

void HSD_FObjStopAnim(HSD_FObj* fobj, void* obj, HSD_ObjUpdateFunc obj_update,
                      f32 rate)
{
    if (fobj == NULL) {
        return;
    }

    FObj_FlushKeyData(fobj, obj, obj_update, rate);
    HSD_FObjSetState(fobj, 0);
}

void HSD_FObjStopAnimAll(HSD_FObj* fobj, void* obj,
                         HSD_ObjUpdateFunc obj_update, f32 rate)
{
    for (; fobj != NULL; fobj = fobj->next) {
        HSD_FObjStopAnim(fobj, obj, obj_update, rate);
    }
}


static thread_local const u8* stream_end;
static u8 readByte(u8** p) {
  if (*p >= stream_end) throw std::runtime_error("truncated animation track");
  return *(*p)++;
}
static f32 parseFloat(u8** p, u8 format) {
  if (format == 0) {
    u32 bits = 0;
    for (unsigned i=0; i<4; ++i) bits |= u32(readByte(p)) << (8*i);
    float value; std::memcpy(&value, &bits, 4);
    if (!std::isfinite(value)) throw std::runtime_error("nonfinite track value");
    return value;
  }
  const unsigned kind = format >> 5;
  int value = readByte(p);
  if (kind == 1 || kind == 2) value |= int(readByte(p)) << 8;
  if (kind == 1 && value >= 32768) value -= 65536;
  if (kind == 3 && value >= 128) value -= 256;
  if (kind < 1 || kind > 4) throw std::runtime_error("unsupported track value format");
  return std::ldexp(float(value), -int(format & 31));
}
static u8 parseOpCode(u8** p) {
  if (*p >= stream_end) throw std::runtime_error("missing track opcode");
  return **p & 15;
}
static u32 parsePackInfo(u8** p) {
  u8 byte = readByte(p);
  u32 count = ((byte >> 4) & 7) + 1;
  for (unsigned shift=3; byte & 128; shift+=7) {
    if (shift > 10) throw std::runtime_error("track packet count overflow");
    byte = readByte(p); count += u32(byte & 127) << shift;
  }
  if (count > 65535) throw std::runtime_error("track packet count overflow");
  return count;
}
static void FObjLaunchKeyData(HSD_FObj* fobj) {
  if (fobj->flags & 0x40) {
    fobj->op_intrp=fobj->op; fobj->flags &= ~0x40;
    fobj->flags |= 0x80; fobj->p0=fobj->p1;
  }
}
static s32 parseWait(u8** p) {
  u32 value = 0;
  for (unsigned shift=0; shift<=14; shift+=7) {
    const u8 byte=readByte(p); value |= u32(byte & 127) << shift;
    if (!(byte & 128)) {
      if (value > 65535) throw std::runtime_error("track wait overflow");
      return value;
    }
  }
  throw std::runtime_error("track wait overflow");
}
static u32 FObjLoadWait(HSD_FObj* fobj)
{
    u32 st = HSD_FObjGetState(fobj);
    HSD_ASSERT(0x16C, st == FOBJ_LOAD_WAIT);

    if ((unsigned) (fobj->ad - fobj->ad_head) >= fobj->length) {
        return 6;
    } else {
        fobj->fterm = parseWait(&fobj->ad);
        fobj->flags |= 0x20;
        return HSD_FObjSetState(fobj, 2);
    }
}

static u32 FObjAnimCON(HSD_FObj* fobj)
{
    u32 st = HSD_FObjGetState(fobj);
    HSD_ASSERT(0x17F, st == FOBJ_LOAD_DATA0 || st == FOBJ_LOAD_DATA);

    fobj->p0 = fobj->p1;
    fobj->p1 = parseFloat(&fobj->ad, fobj->frac_value);
    if (fobj->op_intrp != 5) {
        fobj->d0 = fobj->d1;
        fobj->d1 = 0.0F;
    }

    return HSD_FObjSetState(fobj, st == FOBJ_LOAD_DATA0 ? 3 : 4);
}

static u32 FObjAnimLinear(HSD_FObj* fobj)
{
    u32 st = HSD_FObjGetState(fobj);
    HSD_ASSERT(0x193, st == FOBJ_LOAD_DATA0 || st == FOBJ_LOAD_DATA);

    fobj->p0 = fobj->p1;
    fobj->p1 = parseFloat(&fobj->ad, fobj->frac_value);
    if (fobj->op_intrp != 5) {
        fobj->d0 = fobj->d1;
        fobj->d1 = 0.0F;
    }

    return HSD_FObjSetState(fobj, st == FOBJ_LOAD_DATA0 ? 3 : 4);
}

static u32 FObjAnimSPL0(HSD_FObj* fobj)
{
    u32 st = HSD_FObjGetState(fobj);
    HSD_ASSERT(0x1A7, st == FOBJ_LOAD_DATA0 || st == FOBJ_LOAD_DATA);

    fobj->p0 = fobj->p1;
    fobj->d0 = fobj->d1;
    fobj->p1 = parseFloat(&fobj->ad, fobj->frac_value);
    fobj->d1 = 0.0F;

    return HSD_FObjSetState(fobj, st == FOBJ_LOAD_DATA0 ? 3 : 4);
}

static u32 FObjAnimSPL(HSD_FObj* fobj)
{
    u32 st = HSD_FObjGetState(fobj);
    HSD_ASSERT(0x1B9, st == FOBJ_LOAD_DATA0 || st == FOBJ_LOAD_DATA);

    fobj->p0 = fobj->p1;
    fobj->p1 = parseFloat(&fobj->ad, fobj->frac_value);
    fobj->d0 = fobj->d1;
    fobj->d1 = parseFloat(&fobj->ad, fobj->frac_slope);

    return HSD_FObjSetState(fobj, st == FOBJ_LOAD_DATA0 ? 3 : 4);
}

static u32 FObjAnimSLP(HSD_FObj* fobj)
{
    u32 st = HSD_FObjGetState(fobj);
    HSD_ASSERT(0x1CC, st == FOBJ_LOAD_DATA0 || st == FOBJ_LOAD_DATA);

    fobj->d0 = fobj->d1;
    fobj->d1 = parseFloat(&fobj->ad, fobj->frac_slope);

    return HSD_FObjGetState(fobj);
}

static u32 FObjAnimKey(HSD_FObj* fobj)
{
    u32 st = HSD_FObjGetState(fobj);
    HSD_ASSERT(0x1E9, st == FOBJ_LOAD_DATA0 || st == FOBJ_LOAD_DATA);

    FObjLaunchKeyData(fobj);
    fobj->p1 = parseFloat(&fobj->ad, fobj->frac_value);
    fobj->flags |= 0x40;

    return HSD_FObjSetState(fobj, st == FOBJ_LOAD_DATA0 ? 3 : 4);
}

static inline u32 FObjLoadData(HSD_FObj* fobj)
{
    if ((unsigned) (fobj->ad - fobj->ad_head) >= fobj->length) {
        return 6;
    } else {
        fobj->op_intrp = fobj->op;
        if (fobj->nb_pack == 0) {
            fobj->op = parseOpCode(&fobj->ad);
            fobj->nb_pack = parsePackInfo(&fobj->ad);
        }

        fobj->nb_pack -= 1;

        switch (fobj->op) {
        case HSD_A_OP_CON:
            return FObjAnimCON(fobj);

        case HSD_A_OP_LIN:
            return FObjAnimLinear(fobj);

        case HSD_A_OP_SPL0:
            return FObjAnimSPL0(fobj);

        case HSD_A_OP_SPL:
            return FObjAnimSPL(fobj);

        case HSD_A_OP_SLP:
            return FObjAnimSLP(fobj);

        case HSD_A_OP_KEY:
            return FObjAnimKey(fobj);

        default:
            return 0;
        }
    }
}

void FObjUpdateAnim(HSD_FObj* fobj, void* obj, HSD_ObjUpdateFunc obj_update)
{
    f32 phi_f0;
    HSD_ObjData fobjdata;

    if (obj_update == NULL) {
        return;
    }
    switch (fobj->op_intrp) {
    case HSD_A_OP_KEY:
        if (fobj->flags & 0x80) {
            fobjdata.fv = fobj->p0;
            fobj->flags &= 0xFFFFFF7F;
        } else {
            return;
        }
        break;
    case HSD_A_OP_CON:
        if (fobj->time >= fobj->fterm) {
            phi_f0 = fobj->p1;
        } else {
            phi_f0 = fobj->p0;
        }
        fobjdata.fv = phi_f0;
        break;
    case HSD_A_OP_LIN:
        if (fobj->flags & 0x20) {
            fobj->flags = fobj->flags & 0xFFFFFFDF;
            if (fobj->fterm != 0) {
                fobj->d0 = (fobj->p1 - fobj->p0) / fobj->fterm;
            } else {
                fobj->d0 = 0;
                fobj->p0 = fobj->p1;
            }
        }
        fobjdata.fv = fobj->d0 * fobj->time + fobj->p0;
        break;
    case HSD_A_OP_SPL0:
    case HSD_A_OP_SPL:
    case HSD_A_OP_SLP:
        if (fobj->fterm != 0) {
            fobjdata.fv =
                splGetHelmite(1.0 / fobj->fterm, fobj->time, fobj->p0,
                              fobj->p1, fobj->d0, fobj->d1);
        } else {
            fobjdata.fv = fobj->p1;
        }
        break;
    default:
        return;
    }
    obj_update(obj, fobj->obj_type, &fobjdata);
}

void HSD_FObjInterpretAnim(HSD_FObj* fobj, void* obj,
                           HSD_ObjUpdateFunc obj_update, f32 rate)
{
    f32 fterm;
    u32 state;

    fterm = 0.0F;
    state = fobj != NULL ? HSD_FObjGetState(fobj) : 0;
    if (state != 0 && !(fobj->time += rate, (fobj->time < 0.0))) {
        for (;;) {
            switch (state) {
            case 6: {
                fobj->time += fterm;
                FObjLaunchKeyData(fobj);
                FObjUpdateAnim(fobj, obj, obj_update);
                return;
            }
            case 1:
            case 2: {
                state = FObjLoadData(fobj);
                break;
            }
            case 3: {
                if ((fobj->flags & 0x80) != 0) {
                    FObjUpdateAnim(fobj, obj, obj_update);
                }
                state = FObjLoadWait(fobj);
                break;
            }
            case 4: {
                if (fobj->fterm <= fobj->time) {
                    u8 _[8];
                    state =
#ifdef MUST_MATCH
                        state =
#endif
                            3;

                    fterm = fobj->fterm;
                    fobj->time -= fobj->fterm;
                    HSD_FObjSetState(fobj, state);
                    break;
                }
                FObjUpdateAnim(fobj, obj, obj_update);
                state =
#ifdef MUST_MATCH
                    state =
#endif
                        5;
                HSD_FObjSetState(fobj, state);
                return;
            }
            case 5: {
                state =
#ifdef MUST_MATCH
                    state =
#endif
                        4;
                HSD_FObjSetState(fobj, state);
                break;
            }
            case 0:
                return;
            }
        }
    }
}

void HSD_FObjInterpretAnimAll(void* fobj, void* obj,
                              HSD_ObjUpdateFunc obj_update, f32 rate)
{
    HSD_FObj* fobjNew = (HSD_FObj*) fobj;
    while (fobjNew != NULL) {
        HSD_FObjInterpretAnim(fobjNew, obj, obj_update, rate);
        fobjNew = fobjNew->next;
    }
}


struct Result { float value=0; bool sampled=false; };
void Receive(void* object, u8, HSD_ObjData* data) {
  auto& result=*static_cast<Result*>(object);
  result.value=data->fv; result.sampled=true;
}
} // anonymous namespace
bool SamplePacked(const PackedTrack& track, float frame, float& value, PackedSampleCursor* cursor) {
  if (cursor) cursor->track=nullptr;
  if (!std::isfinite(frame)) throw std::invalid_argument("invalid animation time");
  if (track.size() == 0) return false;
  if (track.size() > 65535) throw std::invalid_argument("oversized fighter track");
  HSD_FObj fobj{};
  fobj.startframe=track.start_frame; fobj.obj_type=track.channel;
  fobj.frac_value=track.value_format; fobj.frac_slope=track.slope_format;
  // The original interpreter only reads byte data; its mutable pointer is local.
  fobj.ad_head=const_cast<u8*>(track.data());
  fobj.length=static_cast<u32>(track.size());
  stream_end=track.data()+track.size();
  HSD_FObjReqAnim(&fobj, frame);
  const float initial_time=fobj.time;
  Result result;
  HSD_FObjInterpretAnim(&fobj, &result, Receive, 0);
  if (cursor && result.sampled && HSD_FObjGetState(&fobj)==5 &&
      fobj.op_intrp>=HSD_A_OP_CON && fobj.op_intrp<=HSD_A_OP_SLP &&
      initial_time>=0 && initial_time<=1048576.f) {
    const float elapsed=initial_time-fobj.time;
    // Every wait is an integer. Within this bound the interpreter's successive
    // subtractions are exact, so target-elapsed reproduces a fresh scan bit for
    // bit. KEY callbacks and finished/inactive tracks retain the original path.
    if (elapsed>=0 && elapsed<=1048576.f && elapsed==float(int32_t(elapsed))) {
      static_assert(sizeof fobj<=sizeof cursor->state,"packed cursor storage");
      std::memcpy(cursor->state,&fobj,sizeof fobj);
      cursor->elapsed_wait=elapsed; cursor->track=&track;
    }
  }
  if (result.sampled) value=result.value;
  return result.sampled;
}
bool SamplePackedFromCursor(const PackedTrack& track, float frame, float& value, const PackedSampleCursor& cursor) {
  if (!std::isfinite(frame)) throw std::invalid_argument("invalid animation time");
  if (cursor.track==&track) {
    HSD_FObj fobj;
    std::memcpy(&fobj,cursor.state,sizeof fobj);
    const float initial_time=float(track.start_frame)+frame;
    const float relative=initial_time-cursor.elapsed_wait;
    if (initial_time>=0 && initial_time<=1048576.f && relative>=0 && relative<fobj.fterm) {
      fobj.time=relative;
      Result result;
      FObjUpdateAnim(&fobj,&result,Receive);
      if (result.sampled) value=result.value;
      return result.sampled;
    }
  }
  return SamplePacked(track,frame,value);
}
}
