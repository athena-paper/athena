//===-- RLConstraint.h ------------------------------------------*- C++ -*-===//
//
//                     The LLVM Compiler Infrastructure
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//
//
// TODO Description
//
//===----------------------------------------------------------------------===//

#ifndef RLCONSTRAINT_H_
#define RLCONSTRAINT_H_

#include "RLConstraints.h"

#include "llvm/ADT/DenseMap.h"
#include "llvm/Support/Casting.h"

namespace deps {

class ConsElem;
class Predicate;

class RLConstraint {
private:
  void printCosntraint(std::string delim = " => ") {
    // llvm::errs() << "pred: " << &pred << "\n";
    // if (&pred) {
    //   pred.dump();
    //   llvm::errs() << "iter\n";
    // }
    if (llvm::isa<RLConstant>(left)) {
      std::string constant;
      llvm::raw_string_ostream *ss = new llvm::raw_string_ostream(constant);
      left->dump(*ss);
      ss->str();
      llvm::errs() << constant;
    } else {
      llvm::errs() << "CE" << left; // address
      llvm::errs() << "[";
      left->dump(llvm::errs()); // description
      llvm::errs() << "]";
    }
    llvm::errs() << delim;
    if (llvm::isa<RLConstant>(right)) {
      std::string constant;
      llvm::raw_string_ostream *ss = new llvm::raw_string_ostream(constant);
      right->dump(*ss);
      ss->str();
      llvm::errs() << constant;
    } else {
      llvm::errs() << "CE" << right;
      llvm::errs() << "[";
      right->dump(llvm::errs());
      llvm::errs() << "]";
    }
    llvm::errs() << info << "\n";
  }

public:
  RLConstraint(const ConsElem &lhs, const ConsElem &rhs, const Predicate &pred,
               bool implicit, std::string info)
      : left(&lhs), right(&rhs), pred(&pred), implicit(implicit), info(info) {
    // if (!implicit)
    DEBUG_WITH_TYPE(DEBUG_TYPE_CONSTRAINT, printCosntraint(););
  }
  RLConstraint(const ConsElem *lhs, const ConsElem *rhs, const Predicate *pred,
               bool implicit, std::string info)
      : left(lhs), right(rhs), pred(pred), implicit(implicit), info(info) {
    // if (!implicit)
    DEBUG_WITH_TYPE(DEBUG_TYPE_CONSTRAINT, printCosntraint(););
  }
  const ConsElem &lhs() const { return *left; }
  const ConsElem &rhs() const { return *right; }
  const Predicate &predicate() const { return *pred; }

  void dump(std::string delim = " <: ") { printCosntraint(delim); }

private:
  const ConsElem *left;
  const ConsElem *right;
  const Predicate *pred;
  bool implicit;
  std::string info;
  friend struct llvm::DenseMapInfo<RLConstraint>;
};

} // namespace deps

#endif /* RLCONSTRAINT_H_ */
