import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  UpdateCachePolicyRequest,
  UpdateCachePolicyResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateCachePolicyCommandInput
  extends UpdateCachePolicyRequest {}
export interface UpdateCachePolicyCommandOutput
  extends UpdateCachePolicyResult,
    __MetadataBearer {}
export declare class UpdateCachePolicyCommand extends $Command<
  UpdateCachePolicyCommandInput,
  UpdateCachePolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateCachePolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateCachePolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<UpdateCachePolicyCommandInput, UpdateCachePolicyCommandOutput>;
  private serialize;
  private deserialize;
}
